-- Disable by default XML import cron
UPDATE
    ir_cron
SET
    active = false
FROM
    ir_cron irc
INNER JOIN ir_model_data irmd
    ON irmd.res_id = irc.id
    AND irmd.model = 'ir.cron'
    AND irmd.module = 'mdc_weight_mgmt_xml_import'
    AND irmd.name = 'ir_cron_mdc_weight_import'
WHERE
    irc.id=ir_cron.id
;

-- Disable by default FTP for lines (equipments)
UPDATE maintenance_equipment SET requires_ftp = false;
