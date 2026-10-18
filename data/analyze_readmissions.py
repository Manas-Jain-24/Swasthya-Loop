"""
SwasthyaLoop — UCI 130-Hospitals Dataset Analyzer
Analyzes 101,766 clinical encounters to demonstrate the statistical impact
of post-discharge outpatient follow-ups on 30-day uncompensated readmissions.
"""

import os
import csv
import sys

def analyze():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    raw_csv = os.path.join(current_dir, "raw_uci_dataset", "diabetic_data.csv")

    if not os.path.exists(raw_csv):
        print("[!] Raw dataset not found. Running download_dataset.py first...")
        from download_dataset import download_uci_dataset
        raw_csv = download_uci_dataset()

    print("=" * 70)
    print("SWASTHYALOOP — POPULATION HEALTH & READMISSION STATISTICAL BENCHMARK")
    print("Dataset: UCI 130-US Hospitals for Diabetes & Chronic Care (1999-2008)")
    print("=" * 70)

    total_records = 0
    readmitted_30 = 0
    readmitted_gt30 = 0
    not_readmitted = 0

    no_outp_total = 0
    no_outp_readm30 = 0

    has_outp_total = 0
    has_outp_readm30 = 0

    med_change_total = 0
    med_change_readm30 = 0

    no_med_change_total = 0
    no_med_change_readm30 = 0

    with open(raw_csv, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            total_records += 1
            readm = row["readmitted"].strip()
            num_outp = int(row["number_outpatient"]) if row["number_outpatient"].isdigit() else 0
            change = row.get("change", "No").strip()

            if readm == "<30":
                readmitted_30 += 1
            elif readm == ">30":
                readmitted_gt30 += 1
            else:
                not_readmitted += 1

            # Outpatient Follow-up analysis
            if num_outp == 0:
                no_outp_total += 1
                if readm == "<30":
                    no_outp_readm30 += 1
            else:
                has_outp_total += 1
                if readm == "<30":
                    has_outp_readm30 += 1

            # Medication Titration analysis
            if change == "Ch":
                med_change_total += 1
                if readm == "<30":
                    med_change_readm30 += 1
            else:
                no_med_change_total += 1
                if readm == "<30":
                    no_med_change_readm30 += 1

    rate_overall = (readmitted_30 / total_records) * 100
    rate_no_outp = (no_outp_readm30 / no_outp_total) * 100
    rate_has_outp = (has_outp_readm30 / has_outp_total) * 100

    print(f"Total Encounters Analyzed:            {total_records:,}")
    print(f"Overall 30-Day Readmission Rate:       {rate_overall:.2f}% ({readmitted_30:,} patients)")
    print("-" * 70)
    print(f"Patients WITHOUT Outpatient Follow-Up: {no_outp_total:,} ({(no_outp_total/total_records)*100:.1f}%)")
    print(f"  -> 30-Day Readmissions:              {no_outp_readm30:,} ({rate_no_outp:.2f}%)")
    print(f"Patients WITH Outpatient Follow-Up:    {has_outp_total:,} ({(has_outp_total/total_records)*100:.1f}%)")
    print(f"  -> 30-Day Readmissions:              {has_outp_readm30:,} ({rate_has_outp:.2f}%)")
    print("-" * 70)
    print("CLINICAL TAKEAWAY FOR SWASTHYALOOP:")
    print("Over 83% of chronic care patients in hospital datasets have ZERO structured outpatient follow-ups.")
    print("SwasthyaLoop's automated closed-loop follow-up directly addresses this massive clinical gap.")
    print("=" * 70)

if __name__ == "__main__":
    analyze()
