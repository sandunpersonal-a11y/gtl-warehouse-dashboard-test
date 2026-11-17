GTL TEST DASHBOARD – ZONE-WISE UPGRADE
=====================================
This is a TEST package only. Do not upload it to the LIVE repository.

FILES:
- index.html: original dashboard design, PWA, charts, plus Overview Floor Level filter
- zone-maps.html: new 7-building zone map explorer
- zone-data.json: 527 records from the uploaded Excel snapshot
- maps/: 11 uploaded warehouse floor map PNG files
- Code_Zonewise_Google_Sheets.gs: optional live Google Sheets Apps Script backend
- existing icons, manifest and other original files retained

DEPLOY TEST:
1. BACK UP the current TEST repository.
2. Upload the CONTENTS of this ZIP to the root of gtl-warehouse-dashboard-test (not the LIVE repo).
3. Wait for GitHub Pages deployment; hard-refresh the TEST URL.
4. Test Overview: Building and FLOOR LEVEL selectors, charts and KPI values.
5. Test Area Availability: same filters should apply.
6. Test Zone Map: choose Building, Floor, Area Status and search zone. Click zone list entries to view values.
7. B1 zones are pending the user's final zone-level data; the 2 summary rows are retained.
8. B3 only Ground Floor. US Lanka 3 map sections are all rented; one summary data row.
9. Negative available balances display as zero; original Excel is unchanged.

LIVE GOOGLE SHEETS:
This package runs immediately from zone-data.json (a fixed Excel snapshot).
To enable automatic updates:
1. Create an Apps Script project for the Google Sheet.
2. Paste Code_Zonewise_Google_Sheets.gs, deploy as Web App per IT security policy.
3. In index.html find GTL_ZONE_CONFIG and set:
   source:"api", apiUrl:"YOUR_DEPLOYED_APPS_SCRIPT_EXEC_URL"
4. Redeploy the TEST repository. The same row schema can later be supplied by the IT API.
Never put private API credentials in GitHub Pages JavaScript.
For authenticated IT APIs, use an approved secure server-side proxy.

IMPORTANT LIMITATION:
Floor maps are static uploaded PNGs, with an interactive zone data list alongside.
Precise clickable polygon overlays directly on the image require coordinate mapping for
each zone; this version does not guess zone coordinates.
For B1, add real zone rows when available; no fictional zone SQFT values are assigned.
