select p.* 
from developer.parcels_in_deposits2 p
join billy.depvalld d on p.old_fig_deposits_record_id = d.id
where d.deposit_date>='2017-03-20'
and p.old_fig_deposits_record_id in (OLDFIGLIST);