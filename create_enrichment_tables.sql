-- Research Engine: Enrichment Tables
-- Run this in the Supabase SQL Editor to create the enrichment schema.

-- 1. Concepts reference table (must exist before article_concepts FK)
CREATE TABLE IF NOT EXISTS concepts (
    name TEXT PRIMARY KEY,
    category TEXT NOT NULL,
    description TEXT
);

-- 2. Article enrichments (one-to-one with research_articles)
CREATE TABLE IF NOT EXISTS article_enrichments (
    id BIGSERIAL PRIMARY KEY,
    article_id BIGINT NOT NULL UNIQUE REFERENCES research_articles(id) ON DELETE CASCADE,
    abstract TEXT,
    key_takeaways TEXT,
    key_findings JSONB DEFAULT '[]'::jsonb,
    mechanistic_reasoning TEXT,
    limitations TEXT,
    methodology TEXT,
    tissue_system TEXT[] DEFAULT '{}',
    joint_region TEXT[] DEFAULT '{}',
    species TEXT,
    domain_tags TEXT[] DEFAULT '{}',
    extraction_confidence TEXT NOT NULL DEFAULT 'MEDIUM'
        CHECK (extraction_confidence IN ('HIGH', 'MEDIUM', 'LOW')),
    needs_manual_review BOOLEAN NOT NULL DEFAULT FALSE,
    review_notes TEXT,
    extracted_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 3. Article-concept junction table
CREATE TABLE IF NOT EXISTS article_concepts (
    id BIGSERIAL PRIMARY KEY,
    article_id BIGINT NOT NULL REFERENCES research_articles(id) ON DELETE CASCADE,
    concept TEXT NOT NULL REFERENCES concepts(name) ON DELETE CASCADE,
    relevance TEXT NOT NULL DEFAULT 'mentioned'
        CHECK (relevance IN ('primary', 'secondary', 'mentioned')),
    UNIQUE (article_id, concept)
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_enrichments_article_id ON article_enrichments(article_id);
CREATE INDEX IF NOT EXISTS idx_enrichments_confidence ON article_enrichments(extraction_confidence);
CREATE INDEX IF NOT EXISTS idx_enrichments_needs_review ON article_enrichments(needs_manual_review) WHERE needs_manual_review = TRUE;
CREATE INDEX IF NOT EXISTS idx_enrichments_methodology ON article_enrichments(methodology);
CREATE INDEX IF NOT EXISTS idx_enrichments_domain_tags ON article_enrichments USING gin(domain_tags);
CREATE INDEX IF NOT EXISTS idx_enrichments_tissue_system ON article_enrichments USING gin(tissue_system);
CREATE INDEX IF NOT EXISTS idx_enrichments_joint_region ON article_enrichments USING gin(joint_region);
CREATE INDEX IF NOT EXISTS idx_concepts_category ON concepts(category);
CREATE INDEX IF NOT EXISTS idx_article_concepts_article ON article_concepts(article_id);
CREATE INDEX IF NOT EXISTS idx_article_concepts_concept ON article_concepts(concept);
CREATE INDEX IF NOT EXISTS idx_article_concepts_relevance ON article_concepts(relevance);

-- Full-text search on key_takeaways and mechanistic_reasoning
CREATE INDEX IF NOT EXISTS idx_enrichments_takeaways_fts
    ON article_enrichments USING gin(to_tsvector('english', COALESCE(key_takeaways, '')));
CREATE INDEX IF NOT EXISTS idx_enrichments_reasoning_fts
    ON article_enrichments USING gin(to_tsvector('english', COALESCE(mechanistic_reasoning, '')));

-- Seed concept vocabulary
INSERT INTO concepts (name, category, description) VALUES
    ('mechanotransduction', 'molecular', 'Conversion of mechanical stimuli into biochemical signals by cells'),
    ('wolffs_law', 'mechanical', 'Bone adapts its structure to the loads placed upon it'),
    ('bifurcation_theory', 'theoretical', 'System transitions between discrete stable states at critical parameter thresholds'),
    ('dissipative_structures', 'theoretical', 'Far-from-equilibrium systems maintained by continuous energy throughput (Prigogine)'),
    ('piezo1', 'molecular', 'Mechanically-activated ion channel; primary mechanosensor in bone, cartilage, endothelium'),
    ('yap_taz', 'molecular', 'Mechanosensitive transcriptional co-activators; nuclear readout of cytoskeletal tension'),
    ('linc_complex', 'molecular', 'Linker of Nucleoskeleton and Cytoskeleton; transmits force to the nucleus'),
    ('apoptosis', 'molecular', 'Programmed cell death; triggered by mechanical underloading or overloading'),
    ('mechanosensing', 'molecular', 'Cellular detection of mechanical forces via membrane proteins and cytoskeleton'),
    ('tensegrity', 'mechanical', 'Structural integrity through balanced tension and compression elements'),
    ('fibrocartilaginous_metaplasia', 'clinical', 'Tendon tissue transformation under chronic compressive loading'),
    ('scapular_dyskinesis', 'clinical', 'Altered scapular position or motion affecting shoulder mechanics'),
    ('critical_shoulder_angle', 'clinical', 'Radiographic measure of lateral acromial extension and glenoid inclination'),
    ('fatty_infiltration', 'clinical', 'Fat accumulation within muscle following denervation or chronic disuse'),
    ('motor_control', 'neural', 'Neural regulation of movement patterns and muscle activation sequencing'),
    ('kinetic_chain', 'mechanical', 'Sequential activation and force transfer through linked body segments'),
    ('force_vectors', 'mechanical', 'Direction and magnitude of forces acting on joint structures'),
    ('stress_shielding', 'mechanical', 'Bone resorption due to reduced mechanical loading (e.g., after implant)'),
    ('bone_remodeling', 'mechanical', 'Coupled osteoclast resorption and osteoblast formation in response to loading'),
    ('tendon_adaptation', 'mechanical', 'Structural and compositional changes in tendon responding to load history'),
    ('cartilage_degeneration', 'clinical', 'Progressive loss of articular cartilage matrix and chondrocyte function'),
    ('inflammation', 'molecular', 'Immune-mediated tissue response; can be triggered by mechanical damage'),
    ('neural_plasticity', 'neural', 'Nervous system reorganization in response to injury or altered input'),
    ('proprioception', 'neural', 'Sensory awareness of joint position and movement'),
    ('viscoelasticity', 'mechanical', 'Time-dependent mechanical behavior of biological tissues'),
    ('creep', 'mechanical', 'Progressive deformation under sustained load'),
    ('fatigue_failure', 'mechanical', 'Tissue failure from repeated sub-threshold loading cycles'),
    ('threshold_behavior', 'theoretical', 'Discrete state transitions occurring at critical parameter values'),
    ('phase_transition', 'theoretical', 'Abrupt change in system state analogous to physical phase changes'),
    ('evolutionary_conservation', 'evolutionary', 'Preservation of molecular or structural features across species over deep time'),
    ('allometry', 'evolutionary', 'Scaling relationships between body size and structural/functional parameters'),
    ('collagen_organization', 'molecular', 'Hierarchical arrangement of collagen fibrils determining tissue mechanical properties'),
    ('mmp_activity', 'molecular', 'Matrix metalloproteinase enzymatic degradation of extracellular matrix'),
    ('enthesis_biology', 'clinical', 'Biology of tendon-bone insertion sites; graded tissue transition zone'),
    ('subacromial_impingement', 'clinical', 'Mechanical compression of rotator cuff between acromion and humeral head'),
    ('glenoid_morphology', 'clinical', 'Shape and version of the glenoid affecting joint stability and loading'),
    ('rotator_cuff_biomechanics', 'mechanical', 'Force couples and load sharing among rotator cuff muscles'),
    ('scapulothoracic_mechanics', 'mechanical', 'Motion and stability of scapula on thoracic wall')
ON CONFLICT (name) DO NOTHING;
