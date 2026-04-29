-- =========================
-- USER DOMAIN
-- =========================
CREATE TABLE users (
    user_id VARCHAR(50) PRIMARY KEY,
    email VARCHAR(255),
    name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE skin_type (
    skin_type_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(50)
);

CREATE TABLE skin_concern (
    concern_id VARCHAR(50) PRIMARY KEY,
    concern_name VARCHAR(100)
);

CREATE TABLE user_skin_profile (
    profile_id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(50) REFERENCES users(user_id),
    skin_type_id VARCHAR(50) REFERENCES skin_type(skin_type_id),
    confidence_score FLOAT,
    recorded_at TIMESTAMP
);

CREATE TABLE user_concern (
    user_id VARCHAR(50) REFERENCES users(user_id),
    concern_id VARCHAR(50) REFERENCES skin_concern(concern_id),
    PRIMARY KEY (user_id, concern_id)
);

-- =========================
-- PRODUCT DOMAIN
-- =========================
CREATE TABLE brand (
    brand_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100),
    country VARCHAR(100)
);

CREATE TABLE routine_category (
    category_id VARCHAR(50) PRIMARY KEY,
    category_name VARCHAR(100),
    step_order INT
);

CREATE TABLE product (
    product_id VARCHAR(50) PRIMARY KEY,
    brand_id VARCHAR(50) REFERENCES brand(brand_id),
    category_id VARCHAR(50) REFERENCES routine_category(category_id),
    name VARCHAR(255),
    price FLOAT
);

CREATE TABLE product_metadata (
    product_id VARCHAR(50) PRIMARY KEY REFERENCES product(product_id),
    rating FLOAT,
    review_count INT,
    popularity_score FLOAT
);

-- =========================
-- INGREDIENT DOMAIN
-- =========================
CREATE TABLE ingredient (
    ingredient_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100),
    inci_name VARCHAR(150)
);

CREATE TABLE product_ingredient (
    product_id VARCHAR(50) REFERENCES product(product_id),
    ingredient_id VARCHAR(50) REFERENCES ingredient(ingredient_id),
    PRIMARY KEY (product_id, ingredient_id)
);
ALTER TABLE product_ingredient 
ADD COLUMN role VARCHAR(50),
ADD COLUMN concentration FLOAT;


CREATE TABLE ingredient_skin_type (
    ingredient_id VARCHAR(50) REFERENCES ingredient(ingredient_id),
    skin_type_id VARCHAR(50) REFERENCES skin_type(skin_type_id),
    effect_type VARCHAR(50),
    PRIMARY KEY (ingredient_id, skin_type_id)
);

CREATE TABLE ingredient_concern (
    ingredient_id VARCHAR(50) REFERENCES ingredient(ingredient_id),
    concern_id VARCHAR(50) REFERENCES skin_concern(concern_id),
    effect_type VARCHAR(50),
    impact_score FLOAT,
    PRIMARY KEY (ingredient_id, concern_id)
);

CREATE TABLE ingredient_conflict (
    ingredient_id_1 VARCHAR(50) REFERENCES ingredient(ingredient_id),
    ingredient_id_2 VARCHAR(50) REFERENCES ingredient(ingredient_id),
    conflict_level VARCHAR(20),
    PRIMARY KEY (ingredient_id_1, ingredient_id_2)
);

INSERT INTO brand (brand_id, name, country) VALUES
('b1', 'Spa Ceylon', 'Sri Lanka'),
('b2', 'Nature’s Secrets', 'Sri Lanka'),
('b3', 'Janet Ayurveda', 'Sri Lanka'),
('b4', 'CeraVe', 'USA'),
('b5', 'The Ordinary', 'Canada'),
('b6', 'COSRX', 'South Korea'),
('b7', 'Cetaphil', 'USA');

INSERT INTO routine_category (category_id, category_name, step_order) VALUES
('rc1', 'Cleanser', 1),
('rc2', 'Serum', 2),
('rc3', 'Moisturizer', 3),
('rc4', 'Mask', 4);

INSERT INTO product (product_id, brand_id, category_id, name, price) VALUES
-- Spa Ceylon
('p1', 'b1', 'rc1', 'Neem & Tea Tree Face Wash', 3200),
('p2', 'b1', 'rc3', 'Aloe Vera Gel', 2800),

-- Nature’s Secrets
('p3', 'b2', 'rc1', 'Papaya Face Wash', 1200),
('p4', 'b2', 'rc3', 'Aloe 94% Gel', 1500),

-- Janet Ayurveda
('p5', 'b3', 'rc4', 'Herbal Face Pack', 1800),

-- CeraVe
('p6', 'b4', 'rc1', 'Foaming Facial Cleanser', 5500),
('p7', 'b4', 'rc3', 'Moisturizing Cream', 7000),

-- The Ordinary
('p8', 'b5', 'rc2', 'Niacinamide 10% + Zinc', 4500),
('p9', 'b5', 'rc2', 'Salicylic Acid 2% Solution', 4800),

-- COSRX
('p10', 'b6', 'rc1', 'Low pH Good Morning Cleanser', 6000),
('p11', 'b6', 'rc2', 'BHA Blackhead Power Liquid', 6500),

-- Cetaphil
('p12', 'b7', 'rc1', 'Gentle Skin Cleanser', 5000);


INSERT INTO ingredient (ingredient_id, name, inci_name) VALUES
('i1', 'Niacinamide', 'Niacinamide'),
('i2', 'Salicylic Acid', 'Salicylic Acid'),
('i3', 'Hyaluronic Acid', 'Sodium Hyaluronate'),
('i4', 'Aloe Vera', 'Aloe Barbadensis Leaf Extract'),
('i5', 'Tea Tree Oil', 'Melaleuca Alternifolia'),
('i6', 'Papaya Extract', 'Carica Papaya Extract'),
('i7', 'Zinc', 'Zinc PCA'),
('i8', 'Centella Asiatica', 'Centella Asiatica Extract');

INSERT INTO product_ingredient (product_id, ingredient_id, role, concentration) VALUES
('p6','i9','solvent',55.0),           -- Water
('p6','i10','surfactant',8.0),        -- Cocamidopropyl Betaine
('p6','i11','surfactant',6.0),        -- Sodium Lauroyl Sarcosinate
('p6','i3','humectant',2.0),          -- Hyaluronic Acid
('p6','i1','active',4.0),             -- Niacinamide
('p6','i12','emollient',3.0),         -- Ceramides
('p6','i13','emulsifier',2.0),        -- Cetearyl Alcohol
('p6','i14','thickener',1.5),         -- Carbomer
('p6','i15','pH adjuster',0.5),       -- Sodium Hydroxide
('p6','i16','preservative',0.8),      -- Phenoxyethanol
('p6','i17','preservative',0.5),      -- Ethylhexylglycerin
('p6','i18','chelating agent',0.2),   -- Disodium EDTA
('p6','i19','soothing',1.0),          -- Allantoin
('p6','i20','humectant',3.0),         -- Glycerin
('p6','i21','stabilizer',1.5);        -- Xanthan Gum

INSERT INTO product_ingredient VALUES
('p8','i9','solvent',70.0),
('p8','i1','active',10.0),
('p8','i7','active',1.0),
('p8','i20','humectant',5.0),
('p8','i14','thickener',1.2),
('p8','i15','pH adjuster',0.5),
('p8','i16','preservative',0.8),
('p8','i17','preservative',0.5),
('p8','i21','stabilizer',1.0);

INSERT INTO product_ingredient VALUES
('p11','i9','solvent',60.0),
('p11','i2','active',4.0),
('p11','i20','humectant',5.0),
('p11','i8','soothing',3.0),
('p11','i22','humectant',4.0),       -- Butylene Glycol
('p11','i23','humectant',3.0),       -- Betaine
('p11','i16','preservative',0.8),
('p11','i17','preservative',0.5),
('p11','i14','thickener',1.0),
('p11','i15','pH adjuster',0.6),
('p11','i18','chelating agent',0.2);

INSERT INTO product_ingredient VALUES
('p12','i9','solvent',65.0),
('p12','i10','surfactant',7.0),
('p12','i24','emollient',5.0),       -- Cetyl Alcohol
('p12','i20','humectant',4.0),
('p12','i25','emollient',3.0),       -- Propylene Glycol
('p12','i16','preservative',0.8),
('p12','i17','preservative',0.5),
('p12','i18','chelating agent',0.2),
('p12','i15','pH adjuster',0.5),
('p12','i21','stabilizer',1.0);

INSERT INTO product_ingredient VALUES
('p1','i9','solvent',58.0),
('p1','i10','surfactant',8.0),
('p1','i5','active',2.5),
('p1','i4','soothing',4.0),
('p1','i26','herbal',3.0),           -- Neem Extract
('p1','i20','humectant',4.0),
('p1','i14','thickener',1.5),
('p1','i16','preservative',0.8),
('p1','i17','preservative',0.5),
('p1','i15','pH adjuster',0.6),
('p1','i21','stabilizer',1.0);

INSERT INTO ingredient VALUES
('i9','Water','Aqua'),
('i10','Cocamidopropyl Betaine','Cocamidopropyl Betaine'),
('i11','Sodium Lauroyl Sarcosinate','Sodium Lauroyl Sarcosinate'),
('i12','Ceramides','Ceramide NP'),
('i13','Cetearyl Alcohol','Cetearyl Alcohol'),
('i14','Carbomer','Carbomer'),
('i15','Sodium Hydroxide','Sodium Hydroxide'),
('i16','Phenoxyethanol','Phenoxyethanol'),
('i17','Ethylhexylglycerin','Ethylhexylglycerin'),
('i18','Disodium EDTA','Disodium EDTA'),
('i19','Allantoin','Allantoin'),
('i20','Glycerin','Glycerin'),
('i21','Xanthan Gum','Xanthan Gum'),
('i22','Butylene Glycol','Butylene Glycol'),
('i23','Betaine','Betaine'),
('i24','Cetyl Alcohol','Cetyl Alcohol'),
('i25','Propylene Glycol','Propylene Glycol'),
('i26','Neem Extract','Azadirachta Indica Extract');

INSERT INTO product_ingredient (product_id, ingredient_id) VALUES
('p2', 'i4'),
('p3', 'i6'),
('p4', 'i4'),
('p7', 'i3'),
('p9', 'i2'),
('p10', 'i8'),
('p12', 'i3');

INSERT INTO skin_type (skin_type_id, name) VALUES
('s1', 'Oily'),
('s2', 'Dry'),
('s3', 'Combination'),
('s4', 'Sensitive');


INSERT INTO skin_concern (concern_id, concern_name) VALUES
('c1', 'Acne'),
('c2', 'Pigmentation'),
('c3', 'Aging'),
('c4', 'Dehydration'),
('c5', 'Sensitivity');


INSERT INTO ingredient_concern (ingredient_id, concern_id, effect_type, impact_score) VALUES
('i1', 'c1', 'oil control', 0.8),
('i1', 'c2', 'brightening', 0.7),
('i2', 'c1', 'acne treatment', 0.9),
('i3', 'c4', 'hydration', 0.9),
('i4', 'c5', 'soothing', 0.8),
('i5', 'c1', 'antibacterial', 0.75),
('i6', 'c2', 'exfoliating', 0.6),
('i8', 'c5', 'calming', 0.85);

INSERT INTO ingredient_skin_type (ingredient_id, skin_type_id, effect_type) VALUES
('i1', 's1', 'excellent'),
('i2', 's1', 'excellent'),
('i3', 's2', 'excellent'),
('i4', 's4', 'good'),
('i5', 's1', 'good'),
('i8', 's4', 'excellent');

INSERT INTO ingredient_conflict (ingredient_id_1, ingredient_id_2, conflict_level) VALUES
('i2', 'i1', 'low'),
('i2', 'i3', 'medium');

INSERT INTO product_metadata (product_id, rating, review_count, popularity_score) VALUES
('p6', 4.5, 1200, 0.90),
('p8', 4.6, 2000, 0.95),
('p11', 4.4, 1500, 0.88),
('p12', 4.3, 800, 0.85);
