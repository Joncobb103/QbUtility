with 
f1 as 
(
	select d.id, d.deposit_id from developer.docv d 
),
f3 as (
	select old_fig_deposits_record_id, case when count(*) > 0 then 'pids generated' end
	as pid_status from developer.parcels_in_deposits2 group by old_fig_deposits_record_id
),
f2 as 
(
	select 
	case when d.id is null then 'No'
	else 'Yes' 
	end
	as document,
	case when r.ocr_text is null then 'No' 
	else 'Yes'
	end as ocr_text
	, o.district_full_name, o.syscountyname, o.id, o.state,o.deposit_amount,o.deposit_date, 
	case when cp.pid_status is null then 'None' else 'has_pids' end as pid_status ,d2.diff,
	case when r.ocr_text ilike '%clerk%' then 'County Clerk'
	else 'Tax collector' 
	end
	as Clerk_doc
	from billy.depvalld o 
	left join developer.rocrv r on o.id = r.deposit_id
    left join developer.depvspid2 d2 on o.id = d2.old_fig_deposits_record_id
	left join f1 d on o.id = d.deposit_id
	left join f3 cp on o.id = cp.old_fig_deposits_record_id
)
select * from f2
where f2.deposit_date >='(REPLACE DATE)'
and state in ('(REPLACE STATE)')
and syscountyname not in ('BANKRUPTCY')
/* and (DFN OR COUNTY) ilike '%(REPLACE COUNTY)%' */
;