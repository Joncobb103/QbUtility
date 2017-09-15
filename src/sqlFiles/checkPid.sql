select d.district_full_name, p.old_fig_deposits_record_id,
p.active_lien_number, p.active_parcel,p.tax_year, p.lien_year,p.block,p.lot,p.qual,
p.total_per_parcel,d.state
from developer.parcels_in_deposits2 p
join billy.depvalld d on p.old_fig_deposits_record_id = d.id
where d.deposit_date >='(REPLACE DATE)'
and d.state in( '(REPLACE STATE)')
--and p.old_fig_deposits_record_id = (REPLACE ID)
/* and d.(DFN OR COUNTY) ilike '%(REPLACE COUNTY)%' */
;