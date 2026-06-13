"""Generate the 50-case pipeline entailment eval dataset."""

from __future__ import annotations

import json
from pathlib import Path

OUTPUT = Path(__file__).resolve().parents[1] / "services" / "eval" / "datasets" / "pipeline_v1.json"

BASE_CASES = json.loads(
    (
        Path(__file__).resolve().parents[1] / "services" / "eval" / "datasets" / "pipeline_v1.json"
    ).read_text(encoding="utf-8")
)

EXTRA_CASES: list[dict[str, str]] = [
    {
        "id": "e011",
        "claim": "Food labels shall bear the common name of the food.",
        "clause_text": "The label of a food shall bear the common or usual name of the food, if any there be.",
        "expected": "ENTAILED",
    },
    {
        "id": "e012",
        "claim": "Net quantity of contents must be declared on the principal display panel.",
        "clause_text": "The net quantity of contents shall be declared on the principal display panel of a food in package form.",
        "expected": "ENTAILED",
    },
    {
        "id": "e013",
        "claim": "Allergen labeling must identify major food allergens in plain language.",
        "clause_text": "The label of a food that is a major food allergen shall identify the allergen source in plain language.",
        "expected": "ENTAILED",
    },
    {
        "id": "e014",
        "claim": "Nutrition facts panel must include serving size and calories.",
        "clause_text": "The nutrition information shall include serving size and calories per serving on the nutrition facts panel.",
        "expected": "ENTAILED",
    },
    {
        "id": "e015",
        "claim": "Organic claims require certification by an accredited certifying agent.",
        "clause_text": "Products labeled as organic shall be certified by an accredited certifying agent under the National Organic Program.",
        "expected": "ENTAILED",
    },
    {
        "id": "e016",
        "claim": "California requires refrigerated foods to be stored at safe temperatures.",
        "clause_text": "Potentially hazardous foods shall be maintained at or below 41 degrees Fahrenheit during storage in California.",
        "expected": "ENTAILED",
    },
    {
        "id": "e017",
        "claim": "Food handlers in California must obtain a valid food safety certificate.",
        "clause_text": "Each food facility shall ensure food handlers obtain a valid food safety certificate as required by California law.",
        "expected": "ENTAILED",
    },
    {
        "id": "e018",
        "claim": "Cross-contamination must be prevented during food preparation.",
        "clause_text": "Food employees shall prevent cross-contamination by separating raw and ready-to-eat foods during preparation.",
        "expected": "ENTAILED",
    },
    {
        "id": "e019",
        "claim": "Handwashing is required before handling ready-to-eat food.",
        "clause_text": "Food employees shall wash hands thoroughly before handling ready-to-eat food or after contamination.",
        "expected": "ENTAILED",
    },
    {
        "id": "e020",
        "claim": "Sanitizer concentration must be verified for warewashing.",
        "clause_text": "The concentration of sanitizer shall be verified for warewashing operations using approved test methods.",
        "expected": "ENTAILED",
    },
    {
        "id": "e021",
        "claim": "Public companies must disclose material risks in annual reports.",
        "clause_text": "Registrants shall disclose material risks and uncertainties in the Management Discussion and Analysis section.",
        "expected": "ENTAILED",
    },
    {
        "id": "e022",
        "claim": "Insider trading rules prohibit trading on material nonpublic information.",
        "clause_text": "Insiders shall not trade securities while in possession of material nonpublic information about the issuer.",
        "expected": "ENTAILED",
    },
    {
        "id": "e023",
        "claim": "Form 8-K must be filed for material corporate events.",
        "clause_text": "Issuers shall file Form 8-K to report material corporate events within the prescribed filing period.",
        "expected": "ENTAILED",
    },
    {
        "id": "e024",
        "claim": "Proxy statements must include executive compensation disclosure.",
        "clause_text": "Proxy statements shall include detailed executive compensation disclosure for named executive officers.",
        "expected": "ENTAILED",
    },
    {
        "id": "e025",
        "claim": "Shelf registration statements require updated prospectus supplements.",
        "clause_text": "Issuers using shelf registration shall file prospectus supplements for material changes to the offering.",
        "expected": "ENTAILED",
    },
    {
        "id": "e026",
        "claim": "Food labels must list trans fat content on the nutrition facts panel.",
        "clause_text": "The nutrition facts panel shall declare trans fat content per serving unless an exemption applies.",
        "expected": "ENTAILED",
    },
    {
        "id": "e027",
        "claim": "Health claims on labels require substantiation and authorization.",
        "clause_text": "Health claims on food labels shall be authorized and substantiated according to applicable regulations.",
        "expected": "ENTAILED",
    },
    {
        "id": "e028",
        "claim": "Country of origin labeling is required for covered commodities.",
        "clause_text": "Covered commodities shall bear country of origin labeling at retail as required by applicable rules.",
        "expected": "ENTAILED",
    },
    {
        "id": "e029",
        "claim": "Infant formula labels must include preparation instructions.",
        "clause_text": "Labels of infant formula shall include preparation instructions and required nutrient information.",
        "expected": "ENTAILED",
    },
    {
        "id": "e030",
        "claim": "Food additives must be approved before use in interstate commerce.",
        "clause_text": "Food additives shall be approved for their intended use before use in interstate commerce.",
        "expected": "ENTAILED",
    },
    {
        "id": "e031",
        "claim": "SEC Form 10-K requires quarterly dividend declarations.",
        "clause_text": "The principal display panel shall be large enough to accommodate mandatory label information.",
        "expected": "NOT_ENTAILED",
    },
    {
        "id": "e032",
        "claim": "California food code requires all restaurants to serve organic menu items.",
        "clause_text": "Food employees shall wash hands thoroughly before handling ready-to-eat food or after contamination.",
        "expected": "NOT_ENTAILED",
    },
    {
        "id": "e033",
        "claim": "Public companies must file aircraft maintenance logs with the FAA.",
        "clause_text": "Nutrition information relating to food shall be provided unless an exemption applies.",
        "expected": "NOT_ENTAILED",
    },
    {
        "id": "e034",
        "claim": "Building permits are required before constructing commercial warehouses.",
        "clause_text": "Ingredients shall be listed in descending order of predominance by weight on the label.",
        "expected": "NOT_ENTAILED",
    },
    {
        "id": "e035",
        "claim": "Refrigerated foods must be stored below 41 degrees Fahrenheit.",
        "clause_text": "Proxy statements shall include detailed executive compensation disclosure for named executive officers.",
        "expected": "NOT_ENTAILED",
    },
    {
        "id": "e036",
        "claim": "Trademark registration requires publication in the Federal Register.",
        "clause_text": "Potentially hazardous foods shall be maintained at or below 41 degrees Fahrenheit during storage in California.",
        "expected": "NOT_ENTAILED",
    },
    {
        "id": "e037",
        "claim": "Aircraft maintenance records must be retained for five years.",
        "clause_text": "The nutrition information shall include serving size and calories per serving on the nutrition facts panel.",
        "expected": "NOT_ENTAILED",
    },
    {
        "id": "e038",
        "claim": "Handwashing is optional when gloves are worn in food preparation.",
        "clause_text": "Food employees shall wash hands thoroughly before handling ready-to-eat food or after contamination.",
        "expected": "NOT_ENTAILED",
    },
    {
        "id": "e039",
        "claim": "Form 8-K filings replace all food labeling requirements.",
        "clause_text": "Issuers shall file Form 8-K to report material corporate events within the prescribed filing period.",
        "expected": "NOT_ENTAILED",
    },
    {
        "id": "e040",
        "claim": "Mining permits must be renewed every year with the EPA.",
        "clause_text": "The principal display panel shall be large enough to accommodate all mandatory label information with clarity and conspicuousness.",
        "expected": "NOT_ENTAILED",
    },
    {
        "id": "e041",
        "claim": "Traceability records are required for high-risk foods under FSMA.",
        "clause_text": "Covered entities shall maintain traceability records for foods on the Food Traceability List.",
        "expected": "ENTAILED",
    },
    {
        "id": "e042",
        "claim": "Preventive controls must be implemented in human food facilities.",
        "clause_text": "Facilities shall implement preventive controls to minimize or prevent hazards requiring control.",
        "expected": "ENTAILED",
    },
    {
        "id": "e043",
        "claim": "Foreign supplier verification programs apply to importers.",
        "clause_text": "Importers shall establish and follow foreign supplier verification programs for imported food.",
        "expected": "ENTAILED",
    },
    {
        "id": "e044",
        "claim": "Sanitation standard operating procedures must be documented.",
        "clause_text": "Establishments shall document sanitation standard operating procedures for food contact surfaces.",
        "expected": "ENTAILED",
    },
    {
        "id": "e045",
        "claim": "Hazard analysis must identify known or reasonably foreseeable hazards.",
        "clause_text": "Facilities shall conduct a hazard analysis to identify known or reasonably foreseeable hazards.",
        "expected": "ENTAILED",
    },
    {
        "id": "e046",
        "claim": "Registration of food facilities with FDA is required before operation.",
        "clause_text": "Food facilities shall register with FDA before beginning operations and renew registration as required.",
        "expected": "ENTAILED",
    },
    {
        "id": "e047",
        "claim": "Recalls must be initiated when food presents a health hazard.",
        "clause_text": "Responsible parties shall initiate recalls when food presents a health hazard or serious adverse health consequences.",
        "expected": "ENTAILED",
    },
    {
        "id": "e048",
        "claim": "Good manufacturing practices require protection against allergen cross-contact.",
        "clause_text": "Manufacturers shall protect against allergen cross-contact through adequate controls and procedures.",
        "expected": "ENTAILED",
    },
    {
        "id": "e049",
        "claim": "Water supply in food plants must be safe and adequate.",
        "clause_text": "The water supply in food plants shall be safe, sanitary, and adequate for intended uses.",
        "expected": "ENTAILED",
    },
    {
        "id": "e050",
        "claim": "Pest exclusion measures must be maintained in food processing areas.",
        "clause_text": "Food processing areas shall maintain pest exclusion measures to protect against contamination.",
        "expected": "ENTAILED",
    },
]


def main() -> None:
    existing_ids = {case["id"] for case in BASE_CASES}
    merged = list(BASE_CASES)
    for case in EXTRA_CASES:
        if case["id"] not in existing_ids:
            merged.append(case)
    merged.sort(key=lambda item: item["id"])
    OUTPUT.write_text(json.dumps(merged, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(merged)} cases to {OUTPUT}")


if __name__ == "__main__":
    main()
