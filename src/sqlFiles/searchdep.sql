select p.*
from developer.parcels_in_deposits2 p
join billy.depvalld d on p.old_fig_deposits_record_id = d.id
where d.id = (REPLACE ID);