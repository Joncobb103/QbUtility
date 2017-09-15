select d.document_name,d.district_full_name, r.ocr_text,o.diff, d.state,r.deposit_amount,d.syscountyname
from developer.docv d
left join developer.rocrv r
on r.deposit_id = d.deposit_id
left join developer.depvspid2 o
on o.old_fig_deposits_record_id = r.deposit_id
where d.deposit_id = (REPLACE ID);