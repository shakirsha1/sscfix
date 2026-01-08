#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Batch Solubility Prediction with Complete Thermochemical Properties

Processes multiple solute-solvent pairs from CSV file.
Includes all Optional Input 2 calculations.

Usage:
    python batch_solubility_complete.py --input molecules.csv --output-dir outputs
"""
import os
import sys
import csv
import argparse
from datetime import datetime
import traceback

# Import from complete prediction script
sys.path.insert(0, os.path.dirname(__file__))
from predict_solubility_complete import predict_solubility, initialize_rmg_database


def process_batch(input_csv, output_dir):
    """
    Process batch predictions with complete thermo calculations
    """
    print("\n" + "="*70)
    print("BATCH SOLUBILITY PREDICTION WITH COMPLETE THERMO")
    print("="*70)
    print(f"Input file:  {input_csv}")
    print(f"Output dir:  {output_dir}")
    print("="*70 + "\n")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Read input CSV
    with open(input_csv, 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    print(f"Found {len(rows)} predictions to process\n")
    
    # Pre-initialize RMG database
    try:
        print("Pre-initializing RMG database...")
        initialize_rmg_database()
        print("✓ Database ready\n")
    except Exception as e:
        print(f"⚠ Warning: Could not pre-initialize database: {e}\n")
    
    # Process each row
    results = []
    success_count = 0
    fail_count = 0
    
    for i, row in enumerate(rows, 1):
        print(f"\n{'='*70}")
        print(f"Processing {i}/{len(rows)}")
        print(f"{'='*70}")
        
        try:
            # Extract input data
            solute = row.get('Solute_SMILES', row.get('solute', '')).strip()
            solvent = row.get('Solvent_SMILES', row.get('solvent', '')).strip()
            temp = float(row.get('Temp', row.get('temperature', 298.15)))
            
            if not solute or not solvent:
                raise ValueError("Missing solute or solvent SMILES")
            
            # Run prediction
            result = predict_solubility(solute, solvent, temp)
            results.append(result)
            success_count += 1
            print(f"✓ Success ({i}/{len(rows)})")
            
        except Exception as e:
            print(f"✗ Failed ({i}/{len(rows)}): {e}")
            traceback.print_exc()
            
            # Add failed result
            results.append({
                'solute_smiles': solute if 'solute' in locals() else 'N/A',
                'solvent_smiles': solvent if 'solvent' in locals() else 'N/A',
                'temperature': temp if 'temp' in locals() else 298.15,
                'logS_method1': 'N/A',
                'logS_method2': 'N/A',
                'dGsolv_kcal': 'N/A',
                'dHsolv_kcal': 'N/A',
                'dSsolv_cal': 'N/A',
                'Hsub_kcal': 'N/A',
                'Cpg_cal': 'N/A',
                'Cps_cal': 'N/A',
                'solubility_g_per_L_m1': 'N/A',
                'solubility_mg_per_L_m1': 'N/A',
                'solubility_g_per_L_m2': 'N/A',
                'solubility_mg_per_L_m2': 'N/A',
                'status': f'Failed: {str(e)[:50]}'
            })
            fail_count += 1
    
    # Save results to CSV
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = os.path.join(output_dir, f'solubility_results_complete_{timestamp}.csv')
    
    print(f"\n{'='*70}")
    print("SAVING RESULTS")
    print(f"{'='*70}")
    
    with open(output_file, 'w', newline='') as f:
        fieldnames = [
            'Solvent_SMILES', 'Solute_SMILES', 'Temp',
            'logS_method1_log10_mol_per_L', 'logS_method2_log10_mol_per_L',
            'dGsolv_kcal_per_mol', 'dHsolv_kcal_per_mol', 'dSsolv_cal_per_K_per_mol',
            'Pred_Hsub298_kcal_per_mol', 'Pred_Cpg298_cal_per_K_per_mol', 'Pred_Cps298_cal_per_K_per_mol',
            'solubility_g_per_L_method1', 'solubility_mg_per_L_method1',
            'solubility_g_per_L_method2', 'solubility_mg_per_L_method2',
            'status'
        ]
        
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for result in results:
            writer.writerow({
                'Solvent_SMILES': result.get('solvent_smiles', ''),
                'Solute_SMILES': result.get('solute_smiles', ''),
                'Temp': result.get('temperature', ''),
                'logS_method1_log10_mol_per_L': result.get('logS_method1', ''),
                'logS_method2_log10_mol_per_L': result.get('logS_method2', ''),
                'dGsolv_kcal_per_mol': result.get('dGsolv_kcal', ''),
                'dHsolv_kcal_per_mol': result.get('dHsolv_kcal', ''),
                'dSsolv_cal_per_K_per_mol': result.get('dSsolv_cal', ''),
                'Pred_Hsub298_kcal_per_mol': result.get('Hsub_kcal', ''),
                'Pred_Cpg298_cal_per_K_per_mol': result.get('Cpg_cal', ''),
                'Pred_Cps298_cal_per_K_per_mol': result.get('Cps_cal', ''),
                'solubility_g_per_L_method1': result.get('solubility_g_per_L_m1', ''),
                'solubility_mg_per_L_method1': result.get('solubility_mg_per_L_m1', ''),
                'solubility_g_per_L_method2': result.get('solubility_g_per_L_m2', ''),
                'solubility_mg_per_L_method2': result.get('solubility_mg_per_L_m2', ''),
                'status': result.get('status', 'Unknown')
            })
    
    print(f"✓ Results saved to: {output_file}")
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    print(f"Total predictions: {len(rows)}")
    print(f"Successful:        {success_count}")
    print(f"Failed:            {fail_count}")
    print(f"Success rate:      {success_count/len(rows)*100:.1f}%")
    print(f"{'='*70}\n")
    
    return output_file


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Batch solubility prediction with complete thermochemical properties'
    )
    parser.add_argument('--input', type=str, required=True,
                      help='Input CSV file with columns: Solute_SMILES, Solvent_SMILES, Temp')
    parser.add_argument('--output-dir', type=str, default='outputs',
                      help='Output directory for results (default: outputs)')
    
    args = parser.parse_args()
    
    try:
        output_file = process_batch(args.input, args.output_dir)
        print(f"✓ Batch processing complete!")
        print(f"✓ Results saved to: {output_file}")
    except Exception as e:
        print(f"✗ Fatal error: {e}")
        traceback.print_exc()
        sys.exit(1)
