import pandas as pd
from typing import List
from .config import get_settings
from .database import db


async def run_recommendation(skin_type_id: str, concern_ids: List[str], budget: float):
    settings = get_settings()
    # 1. Fetch raw data
    query_products = """
        SELECT p.product_id, p.name, p.price, b.name as brand, rc.category_name as category, rc.step_order,
               pm.rating, pm.popularity_score
        FROM product p
        JOIN brand b ON p.brand_id = b.brand_id
        JOIN routine_category rc ON p.category_id = rc.category_id
        LEFT JOIN product_metadata pm ON p.product_id = pm.product_id
        WHERE p.price <= $1
    """
    products_records = await db.fetch(query_products, budget)
    if not products_records:
        return []

    # Get product IDs to filter ingredient fetch
    product_ids = [r['product_id'] for r in products_records]
    
    # 2. Fetch ingredients
    # We fetch all ingredients for products in budget
    # PostgreSQL syntax for ANY array
    query_ingredients = """
        SELECT pi.product_id, pi.ingredient_id, pi.role, pi.concentration,
               ic.concern_id, ic.impact_score,
               ist.skin_type_id, ist.effect_type
        FROM product_ingredient pi
        LEFT JOIN ingredient_concern ic ON pi.ingredient_id = ic.ingredient_id
        LEFT JOIN ingredient_skin_type ist ON pi.ingredient_id = ist.ingredient_id
        WHERE pi.product_id = ANY($1)
    """
    ingredients_records = await db.fetch(query_ingredients, product_ids)
    
    # 3. Fetch conflicts
    query_conflicts = "SELECT ingredient_id_1, ingredient_id_2, conflict_level FROM ingredient_conflict"
    conflicts_records = await db.fetch(query_conflicts)
    
    # Process into Pandas
    df_p = pd.DataFrame(products_records)
    df_p['rating'] = df_p['rating'].astype(float).fillna(0)
    df_p['popularity_score'] = df_p['popularity_score'].astype(float).fillna(0)
    
    df_i = pd.DataFrame(ingredients_records)
    
    # Compute concern score per product
    # Filter only relevant concerns
    if not df_i.empty:
        # Concern Score
        rel_concerns = df_i[df_i['concern_id'].isin(concern_ids)].copy()
        # Add basic score calculation. Using concentration safely:
        rel_concerns['concentration'] = rel_concerns['concentration'].astype(float).fillna(1.0)
        rel_concerns['impact_score'] = rel_concerns['impact_score'].astype(float).fillna(0.0)
        
        # calculate partial score
        rel_concerns['partial_score'] = rel_concerns['impact_score'] * (rel_concerns['concentration'] / 100.0)
        
        concern_scores = rel_concerns.groupby('product_id')['partial_score'].sum().reset_index(name='concern_score')
        
        # Skin type formulation (count of active friendly vs total)
        rel_skin = df_i[df_i['skin_type_id'] == skin_type_id]
        skin_scores = rel_skin.groupby('product_id').size().reset_index(name='skin_score') # Simplified
        
        # Merge back
        df_p = df_p.merge(concern_scores, on='product_id', how='left')
        df_p = df_p.merge(skin_scores, on='product_id', how='left')
        
    df_p['concern_score'] = df_p.get('concern_score', pd.Series(0, index=df_p.index)).fillna(0)
    df_p['skin_score'] = df_p.get('skin_score', pd.Series(0, index=df_p.index)).fillna(0)
    
    # Normalize scales to 0-1 safely
    def normalize(series):
        if series.max() == series.min():
            return pd.Series(0, index=series.index)
        return (series - series.min()) / (series.max() - series.min() + 1e-5)
    
    df_p['concern_score_n'] = normalize(df_p['concern_score'])
    df_p['skin_score_n'] = normalize(df_p['skin_score'])
    df_p['rating_n'] = normalize(df_p['rating'])
    df_p['popularity_score_n'] = normalize(df_p['popularity_score'])
    
    df_p['final_score'] = (
        df_p['concern_score_n'] * settings.reco_concern_weight +
        df_p['skin_score_n'] * settings.reco_skin_weight +
        df_p['rating_n'] * settings.reco_rating_weight +
        df_p['popularity_score_n'] * settings.reco_popularity_weight
    )
    
    # Conflicts Penalty
    penalty_map = {"low": 0.05, "medium": 0.1, "high": 0.2}
    conflicts = conflicts_records
    
    for idx, row in df_p.iterrows():
        p_id = row['product_id']
        p_ingredients = df_i[df_i['product_id'] == p_id]['ingredient_id'].unique() if not df_i.empty else []
        
        penalty = 0.0
        for c in conflicts:
            if c['ingredient_id_1'] in p_ingredients and c['ingredient_id_2'] in p_ingredients:
                penalty += penalty_map.get(c['conflict_level'], 0.05)
                
        df_p.at[idx, 'final_score'] -= penalty

    df_p['final_score'] = df_p['final_score'].clip(lower=0)

    # Sort descending
    df_p = df_p.sort_values(by='final_score', ascending=False)
    
    # Prepare result picking best from each category step
    # Realism approach: Return a routine
    # Group by category and pick top
    
    result = []
    # Drop duplicates by category, keeping largest score
    best_routine = df_p.drop_duplicates(subset=['category'], keep='first').sort_values('step_order')
    
    for _, row in best_routine.iterrows():
        reasoning = f"Good match for your skin type."
        if row['concern_score'] > 0:
            reasoning = "Contains effective ingredients for your chosen concerns."
            
        result.append({
            "product_id": row['product_id'],
            "name": row['name'],
            "brand": row['brand'],
            "category": row['category'],
            "price": float(row['price']),
            "score": round(float(row['final_score']), 2),
            "reasoning": reasoning
        })
        
    return result
