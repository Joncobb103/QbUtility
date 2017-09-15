select r.* 
from developer.rocrv r 
left join developer.parcels_in_deposits2 p on p.old_fig_deposits_record_id = r.deposit_id 
join billy.depvalld d on r.deposit_id = d.id 
where r.deposit_date='(REPLACE DATE)' 
and d.syscountyname in
(
'ADAMS'
,'ALAMOSA'
,'ARAPAHOE'
,'ARCHULETA'
,'DOUGLAS'
,'DENVER'
,'EAGLE'
,'GRAND'
,'EL_PASO'
,'GARFIELD'
,'JEFFERSON'
,'LA_PLATA'
,'MESA'
,'MORGAN'
,'PARK'
,'PUEBLO'
,'PITKIN'
,'ROUTT'
,'TELLER'
,'WELD'
)
and p.old_fig_deposits_record_id is null 
and d.state='CO' 
;
