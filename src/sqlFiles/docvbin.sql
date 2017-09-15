select d.document_binary, d.document_name
from developer.docv d
where d.deposit_id = (REPLACE ID);