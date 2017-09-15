select r.district_full_name, r.deposit_id from developer.rocrv r
join developer.docv d on d.deposit_id = r.deposit_id 
where r.deposit_date >= '(REPLACE DATE)'
and d.state in ('(REPLACE STATE)')
and r.ocr_text ilike '%clerk%'
/* and d.(DFN OR COUNTY) ilike '%(REPLACE COUNTY)%' */

;