# Traceability

## Success criterion → evidence → steps
| SC | Tests / checks / gates | Steps | Claims / decisions |
|---|---|---|---|
| SC-1 probe | T-U13, T-U14, T-U17, T-I01, T-I09, G-003 | S-003, S-005, S-006, S-008, S-012 | C-005, C-020, D-012, D-014 |
| SC-2 DTCs + MIL | T-U01..T-U05, T-U09, T-U10, T-U26, T-I02, T-I03, T-I10, G-003 | S-004, S-006, S-008, S-012 | C-014, D-013 |
| SC-3 live data | T-U06..T-U08, T-U11, T-U12, T-I04, T-I05, T-O09, T-P01, T-P02, G-003 | S-004, S-006, S-008, S-012 | C-009, C-011, C-015, D-019 |
| SC-4 vehicle info + report | T-U15, T-U16, T-U21, T-U22, T-U24, T-I06, T-I08, T-I10, T-S10, T-O08 | S-004, S-006, S-007, S-008 | D-013, D-016 |
| SC-5 robustness | T-U18, T-U19, T-U20, T-O01..T-O07, T-O10 | S-003, S-005, S-006, S-008 | D-012, D-014, D-017 |
| SC-6 read-only + privacy | T-S01..T-S04, T-S06..T-S09, T-U23, T-U25, T-I09, CHK-03 | S-002, S-005, S-007, S-008, S-010 | A-005, C-022, D-008, D-011 |
| SC-7 stretch gated | T-S05, T-S11, T-S12, T-U27, G-004 | S-002, S-009, S-014 | C-016, D-018 |
| SC-8 transcript | T-I07 | S-005 | D-015 |
| SC-9 hardware ranking | plan/HARDWARE.md, CHK-04, G-002a, G-003 | S-011, S-012 | C-001..C-005, C-010, C-011, C-017..C-019 |
| SC-10 Windows | T-O02, T-O04 (portable path), G-003 (Windows run) | S-005, S-008, S-012 | A-008, C-012, D-012 |

## Test → requirement
| Test | SC | Test | SC | Test | SC |
|---|---|---|---|---|---|
| T-U01 | SC-2 | T-U19 | SC-5 | T-S01 | SC-6 |
| T-U02 | SC-2 | T-U20 | SC-4, SC-5 | T-S02 | SC-6 |
| T-U03 | SC-2 | T-U21 | SC-4 | T-S03 | SC-6 |
| T-U04 | SC-2 | T-U22 | SC-4 | T-S04 | SC-6 |
| T-U05 | SC-2 | T-U23 | SC-6 | T-S05 | SC-7 |
| T-U06 | SC-3 | T-U24 | SC-4 | T-S06 | SC-6 |
| T-U07 | SC-3 | T-U25 | SC-6 | T-S07 | SC-6 |
| T-U08 | SC-3 | T-U26 | SC-2 | T-S08 | SC-6 |
| T-U09 | SC-2 | T-U27 | SC-7 | T-S09 | SC-6 |
| T-U10 | SC-2 | T-I01 | SC-1 | T-S10 | SC-4 |
| T-U11 | SC-3 | T-I02 | SC-2 | T-S11 | SC-7 |
| T-U12 | SC-3 | T-I03 | SC-2 | T-S12 | SC-7 |
| T-U13 | SC-1 | T-I04 | SC-3 | T-O01 | SC-5 |
| T-U14 | SC-1 | T-I05 | SC-3 | T-O02 | SC-5, SC-10 |
| T-U15 | SC-4 | T-I06 | SC-4 | T-O03 | SC-5 |
| T-U16 | SC-4 | T-I07 | SC-8 | T-O04 | SC-5, SC-10 |
| T-U17 | SC-1 | T-I08 | SC-1..SC-4, SC-6 | T-O05 | SC-5 |
| T-U18 | SC-5 | T-I09 | SC-1, SC-4 | T-O06 | SC-5 |
| T-P01 | SC-3 | T-I10 | SC-2, SC-4, SC-6 | T-O07 | SC-5 |
| T-P02 | SC-3 | | | T-O08 | SC-4 |
| | | | | T-O09 | SC-3 |
| | | | | T-O10 | SC-5 |
