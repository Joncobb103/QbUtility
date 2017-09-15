select syscountyname, district_full_name, state, deposit_id from developer.docv
where deposit_date = '(REPLACE DATE)'
and state in ('(REPLACE STATE)');