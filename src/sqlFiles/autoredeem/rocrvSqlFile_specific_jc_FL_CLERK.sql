select r.* 
from developer.rocrv r 
left join developer.parcels_in_deposits2 p on p.old_fig_deposits_record_id = r.deposit_id 
join billy.depvalld d on r.deposit_id = d.id 
where r.deposit_date='(REPLACE DATE)' 
and r.ocr_text ilike '%clerk%' 
and d.syscountyname IN (
'CHARLOTTE'
,'HERNANDO'
,'LAKE'
,'LEON'
,'MARION'
,'HILLSBOROUGH'
,'MARTIN'
,'OKALOOSA'
,'PINELLAS'
,'POLK'
,'STLUCIE'
,'VOLUSIA'
) 
and p.old_fig_deposits_record_id is null 
and d.state='FL' 
;
