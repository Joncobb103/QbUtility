select r.* 
from developer.rocrv r 
left join developer.parcels_in_deposits2 p on p.old_fig_deposits_record_id = r.deposit_id 
join billy.depvalld b on b.id = r.deposit_id 
where b.deposit_date='(REPLACE DATE)' 
and p.old_fig_deposits_record_id is null 
and r.ocr_text is null 
and b.state in ('AZ') 
and b.syscountyname not in (
'PALMBEACH'
,'MIAMIDADE'
,'PIMA'
,'MESA'
,'UNKNOWN'
,'WALTON'
,'BANKRUPTCY'
) 
and deposit_id in (select deposit_id from developer.docv where deposit_date ='(REPLACE DATE)')
;
