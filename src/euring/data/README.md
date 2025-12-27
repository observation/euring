# EURING Reference Data

This folder contains packaged EURING reference data used at runtime. All files here are JSON and are loaded
directly by the library.

## Data sources

- Species codes: https://www.euring.org/files/documents/EURING_SpeciesCodes_IOC15_1.csv
- Place codes: https://www.euring.org/files/documents/ECPlacePipeDelimited_0.csv
- Schemes: https://app.bto.org/euringcodes/schemes.jsp?check1=Y&check2=Y&check3=Y&check4=Y&orderBy=SCHEME_CODE
- Circumstances: https://app.bto.org/euringcodes/circumstances.jsp
- All other code tables are derived from [EURING – The European Union for Bird Ringing (2020). The EURING Exchange Code 2020. Helsinki, Finland. (PDF v202, 13 Nov 2024)](https://euring.org/data-and-codes/euring-codes)

## Refreshing data

- Update schemes/circumstances via the fetch helper and write JSON to this folder:

```bash
python -m euring.data.fetch --output-dir src/euring/data
```

- Species/place updates are currently maintained in JSON form:
  - `species.json` generated from the EURING species CSV.
  - `places.json` generated from the EURING place code CSV.

If you refresh those sources, regenerate the JSON tables in this folder.
