select syscountyname, district_full_name, state, id as deposit_id from billy.depvalld
and district_full_name ilike '%(REPLACE DFN)%';