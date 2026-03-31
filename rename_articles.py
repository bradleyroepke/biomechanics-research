#!/usr/bin/env python3
"""
Rename misnamed PDFs in Articles/ to follow Year_Author_Journal_Title.pdf convention.
Generates a rename map, prints it for review, and executes renames.
"""

import os
from pathlib import Path

ARTICLES_DIR = Path(__file__).parent / "Articles"

# Manual rename map: old_filename -> new_filename
# Derived from PDF metadata and first-page text
RENAMES = {
    "00007256-200737020-00004.pdf":
        "2007_Folland_SportsMed_Adaptations_to_Strength_Training_Morphological_Neurological.pdf",

    "1-s2.0-S0363502313016018-main.pdf":
        "2014_Nimura_JHandSurg_Joint_Capsule_Attachment_ECRB_Lateral_Epicondylitis.pdf",

    "1-s2.0-S0966636297000386-main.pdf":
        "1998_Novacheck_GaitPosture_Biomechanics_of_Running.pdf",

    "1-s2.0-S1058274617306638-main.pdf":
        "2018_Hwang_JSES_Axial_Load_Transmission_Elbow_Forearm_Rotation.pdf",

    "1-s2.0-S1413355518310761-main.pdf":
        "2019_Neumann_BrazJPhysTher_Scapulothoracic_Muscles_Serratus_Anterior.pdf",

    "13075_2015_Article_738.pdf":
        "2015_Teichtahl_ArthritisResTher_Wolffs_Law_Early_Knee_Osteoarthritis.pdf",

    "1741-7015-10-95.pdf":
        "2012_Oliva_BMCMed_Physiopathology_Intratendinous_Calcific_Deposition.pdf",

    "60381_1.pdf":
        "2009_Coombes_BJSM_Integrative_Model_Lateral_Epicondylalgia.pdf",

    "7-11.pdf":
        "2013_Docking_MLTJ_Relationship_Compressive_Loading_ECM_Changes_Tendons.pdf",

    "B_ABME.0000017544.36001.8e.pdf":
        "2004_Liu_AnnBiomedEng_Polymeric_Scaffolds_Bone_Tissue_Engineering.pdf",

    "Calcific tendinopathy.pdf":
        "1997_Uhthoff_JAAOS_Calcific_Tendinopathy_Rotator_Cuff.pdf",

    # DUPLICATE of 1934_Codman_The_Shoulder.pdf — delete
    # "Codman - The Shoulder.pdf"

    "Journal Cellular Physiology - 2007 - Caplan - Adult mesenchymal stem cells for tissue engineering versus regenerative.pdf":
        "2007_Caplan_JCellPhysiol_Adult_Mesenchymal_Stem_Cells_Tissue_Engineering.pdf",

    "Journal Orthopaedic Research - 2014 - Gerber - Supraspinatus tendon load during abduction is dependent on the size of the.pdf":
        "2014_Gerber_JOrthopRes_Supraspinatus_Tendon_Load_Critical_Shoulder_Angle.pdf",

    "Kannus.pdf":
        "1991_Kannus_JBJS_Histopathological_Changes_Spontaneous_Rupture_Tendons.pdf",

    "Kuhn_throwing the shoulder and human evolution.pdf":
        "2016_Kuhn_AmJOrthop_Throwing_Shoulder_Human_Evolution.pdf",

    "Louis_1997_Unknown_THE_ROTATOR_CUFF,_PART_I.pdf":
        "1997_Soslowsky_OrthopClinNorthAm_Biomechanics_Rotator_Cuff.pdf",

    "Mechanotherapy.pdf":
        "2009_Khan_BJSM_Mechanotherapy_Exercise_Promotes_Tissue_Repair.pdf",

    # DUPLICATE of 1985_Grace — delete
    # "Muscle Imbalance and Extremity Injury_A Perplexing Relationship.pdf"

    "Muscle and Nerve - 2000 - Lieber - Functional and clinical significance of skeletal muscle architecture.pdf":
        "2000_Lieber_MuscleNerve_Skeletal_Muscle_Architecture_Functional_Significance.pdf",

    "PIIS0092867406009615.pdf":
        "2006_Engler_Cell_Matrix_Elasticity_Directs_Stem_Cell_Lineage.pdf",

    "Rockwood and Matsen - The Shoulder, 4th Edition.pdf":
        "2009_Rockwood_Matsen_Book_The_Shoulder_4th_Edition.pdf",

    "STAM_2024_ActaOrthop_ACTA_ORTHOPAEDICA_et_TRAUMATOLOGICA_TURCICA.pdf":
        "2024_Stam_ActaOrthopTraumatTurc_Scapular_Dyskinesia_Winging.pdf",

    "STEM CELLS - 2009 - Chamberlain - Concise Review  Mesenchymal Stem Cells  Their Phenotype  Differentiation Capacity .pdf":
        "2009_Chamberlain_StemCells_Mesenchymal_Stem_Cells_Phenotype_Differentiation.pdf",

    "Scandinavian Med Sci Sports - 2008 - Kannus - Structure of the tendon connective tissue.pdf":
        "2000_Kannus_ScandJMedSciSports_Structure_Tendon_Connective_Tissue.pdf",

    # DUPLICATE of 1991_Warner — delete
    # "Scapulothoracic motion_Moire analysis.pdf"

    "Thomopoulos_tendon to bone healing abstract.pdf":
        "2002_Thomopoulos_ORS_Tendon_Bone_Healing_Postoperative_Activity.pdf",

    "Wolffs_Law_Bone_Functional_Adaptation_Overview.pdf":
        "2016_Chen_BioMedResInt_Wolffs_Law_Bone_Functional_Adaptation.pdf",

    "alfredson-et-al-1998-heavy-load-eccentric-calf-muscle-training-for-the-treatment-of-chronic-achilles-tendinosis.pdf":
        "1998_Alfredson_AmJSportsMed_Heavy_Load_Eccentric_Achilles_Tendinosis.pdf",

    "bjsports-2015-095422.pdf":
        "2016_Cook_BJSM_Revisiting_Continuum_Model_Tendon_Pathology.pdf",

    "current_concepts_review___tendinosis_of_the_elbow.14.pdf":
        "1999_Kraushaar_JBJS_Tendinosis_Elbow_Tennis_Elbow.pdf",

    # DUPLICATE of Kannus.pdf (same MD5) — delete
    # "histopathological_changes_preceding_spontaneous.9.pdf"

    "humeroscapular motion_romeo.pdf":
        "1998_Romeo_Unknown_Humeroscapular_Motion.pdf",

    "ingber_annalsmed03.pdf":
        "2003_Ingber_AnnMed_Mechanobiology_Disease_Mechanotransduction.pdf",

    "nature14288.pdf":
        "2015_Collins_Nature_Reducing_Energy_Cost_Walking_Unpowered_Exoskeleton.pdf",

    "nrm1890.pdf":
        "2006_Vogel_NatRevMolCellBiol_Local_Force_Shape_Change_Cell_Biology.pdf",

    "nrm2594.pdf":
        "2009_Jaalouk_NatRevMolCellBiol_Mechanotransduction_Gone_Awry.pdf",

    "nrm2597.pdf":
        "2009_Wang_NatRevMolCellBiol_Mechanotransduction_at_a_Glance.pdf",

    "predictors_of_scapular_notching_in_patients.16.pdf":
        "2007_Simovitch_JBJS_Predictors_Scapular_Notching_Reverse_TSA.pdf",

    "proske-gandevia-2012-the-proprioceptive-senses-their-roles-in-signaling-body-shape-body-position-and-movement-and.pdf":
        "2012_Proske_PhysiolRev_Proprioceptive_Senses_Body_Shape_Position_Movement.pdf",

    "regan-et-al-1992-microscopic-histopathology-of-chronic-refractory-lateral-epicondylitis.pdf":
        "1992_Regan_AmJSportsMed_Microscopic_Histopathology_Lateral_Epicondylitis.pdf",

    "scapular_dyskinesis_and_its_relation_to_shoulder.8.pdf":
        "2003_Kibler_JAAOS_Scapular_Dyskinesis_Relation_Shoulder_Pain.pdf",

    "tendon_injury_and_tendinopathy__healing_and_repair.30.pdf":
        "2005_Sharma_JBJS_Tendon_Injury_Tendinopathy_Healing_Repair.pdf",

    "tennis_elbow__the_surgical_treatment_of_lateral.5.pdf":
        "1979_Nirschl_JBJS_Surgical_Treatment_Lateral_Epicondylitis.pdf",

    "the_stabilizing_system_of_the_spine__part_i_.1.pdf":
        "1992_Panjabi_JSpinalDisord_Stabilizing_System_Spine.pdf",

    "tuoheti-et-al-2005-contact-area-contact-pressure-and-pressure-patterns-of-the-tendon-bone-interface-after-rotator-cuff.pdf":
        "2005_Tuoheti_AmJSportsMed_Contact_Pressure_Tendon_Bone_Interface_RCR.pdf",

    "wang (2006) mechanobiology of tendon.pdf":
        "2006_Wang_JBiomech_Mechanobiology_of_Tendon.pdf",
}

# Confirmed duplicates (identical MD5 to properly-named files already in collection)
DUPLICATES_TO_DELETE = [
    "Muscle Imbalance and Extremity Injury_A Perplexing Relationship.pdf",       # = 1985_Grace
    "Scapulothoracic motion_Moire analysis.pdf",                                 # = 1991_Warner
    "histopathological_changes_preceding_spontaneous.9.pdf",                     # = Kannus.pdf (both renamed)
    "Codman - The Shoulder.pdf",                                                 # = 1934_Codman_The_Shoulder.pdf
    "1976_Poppen_JBJS_Normal and abnormal motion of the shoulder.pdf",           # = 1976_Poppen_JBJS_Normal_Abnormal_Motion_Shoulder_Article.pdf
    "1977_Poppen_CORR_Forces at the Glenohumeral Joint in Abduction.pdf",       # = 1978_Poppen_CORR_Forces_Glenohumeral_Joint_Abduction.pdf
]


def main():
    # Verify all source files exist
    missing = []
    for old_name in RENAMES:
        if not (ARTICLES_DIR / old_name).exists():
            missing.append(old_name)

    if missing:
        print(f"WARNING: {len(missing)} source files not found:")
        for m in missing:
            print(f"  {m}")
        print()

    # Check for conflicts with existing files
    conflicts = []
    for old_name, new_name in RENAMES.items():
        target = ARTICLES_DIR / new_name
        if target.exists() and old_name != new_name:
            conflicts.append((old_name, new_name))

    if conflicts:
        print(f"WARNING: {len(conflicts)} target names already exist:")
        for old, new in conflicts:
            print(f"  {old} -> {new} (EXISTS)")
        print()

    # Print rename plan
    print(f"{'='*80}")
    print(f"RENAME PLAN: {len(RENAMES)} files")
    print(f"{'='*80}")
    for old_name, new_name in sorted(RENAMES.items()):
        if (ARTICLES_DIR / old_name).exists():
            status = "CONFLICT" if (ARTICLES_DIR / new_name).exists() else "OK"
            print(f"  [{status}] {old_name[:50]}")
            print(f"       -> {new_name}")
    print()

    # Execute renames
    renamed = 0
    skipped = 0
    for old_name, new_name in RENAMES.items():
        src = ARTICLES_DIR / old_name
        dst = ARTICLES_DIR / new_name
        if not src.exists():
            continue
        if dst.exists() and src != dst:
            # Mark as duplicate - append _dup to avoid overwrite
            print(f"  SKIP (target exists): {old_name}")
            skipped += 1
            continue
        os.rename(src, dst)
        renamed += 1

    # Delete confirmed duplicates
    deleted = 0
    for dup in DUPLICATES_TO_DELETE:
        dup_path = ARTICLES_DIR / dup
        if dup_path.exists():
            os.remove(dup_path)
            print(f"  DELETED duplicate: {dup}")
            deleted += 1

    print(f"\nDone: {renamed} renamed, {skipped} skipped, {deleted} duplicates deleted")


if __name__ == '__main__':
    main()
