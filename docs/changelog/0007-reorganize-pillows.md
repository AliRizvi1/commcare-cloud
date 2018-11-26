# 7. Reorganize pillows

**Date:** 2018-11-26

**Optional per env:** No

## CommCare Version Dependency
This version of CommCare must be deployed before rolling out this change:
[todo](https://github.com/dimagi/commcare-hq/commit/todo)


## Change Context
Pillows read changes from kafka and do various processing such as sending  to
elasticsearch, transforming into a UCR table row etc. A doc for same change is read
multiple times for each processor, since there are pillows for each processor.
This is inefficient, so we have combined multiple processors that apply for a
given document type (also called `KAFKA_TOPIC`) such as form/case/user under
one pillow. For e.g. A new single `get_ucr_es_case_pillow` pillow replaces
various old pillows that process case changes such as `CaseToElasticsearchPillow`,
`CaseSearchToElasticsearchPillow`, `ReportCaseToElasticsearchPillow`,
and `kafka-ucr-main` etc. 

## Details
This change replaces old pillows with new pillows. New pillows start
processing at the oldest change of all of old pillows to ensure all changes
are processed by all processors. So initially some changes may be reprocessed for some 
processors, so it will be prudent to make sure that there is
no large difference in checkpoints between the pillows to be reorganized.
This can be checked by dry running step 3 of update steps below at anytime.

Exact reorganization is as per below.

Old Pillow | New Pillow
-- | --
CaseToElasticsearchPillow | get_ucr_es_case_pillow
CaseSearchToElasticsearchPillow | get_ucr_es_case_pillow
kafka-ucr-static | get_ucr_es_case_pillow, get_ucr_es_form_pillow, get_user_es_ucr_pillow
XFormToElasticsearchPillow | get_ucr_es_form_pillow
FormSubmissionMetadataTrackerPillow | get_ucr_es_form_pillow
kafka-ucr-main | get_ucr_es_case_pillow, get_ucr_es_form_pillow, get_user_es_ucr_pillow
AppDbChangeFeedPillow | No Change
ApplicationToElasticsearchPillow | No Change
CacheInvalidatePillow | No Change
DefaultChangeFeedPillow | No Change
DomainDbKafkaPillow | No Change
FarmerRecordFluffPillow | No Change
GeographyFluffPillow | No Change
GroupPillow | get_group_es_pillow
GroupToUserPillow | get_group_es_pillow
KafkaDomainPillow | No Change
LedgerToElasticsearchPillow | No Change
M4ChangeFormFluffPillow | No Change
ReportCaseToElasticsearchPillow | get_ucr_es_case_pillow
ReportXFormToElasticsearchPillow | get_ucr_es_form_pillow
SqlSMSPillow | No Change
UCLAPatientFluffPillow | No Change
UnknownUsersPillow | get_ucr_es_form_pillow
UpdateUserSyncHistoryPillow | No Change
UserCacheInvalidatePillow | No Change
UserGroupsDbKafkaPillow | No Change
UserPillow | get_user_es_ucr_pillow  (includes user UCR processor)

## Steps to update
Ensure that you have deployed a version of CommCare later than the version mentioned above
and that none of pillows for a given document type are too far behind from each other.

1. Replace old pillows with new pillows in pillow section of your app_processes.yml
   Here's an example [pull request](https://github.com/dimagi/commcare-cloud/pull/2415)
   Do not merge this until the switch is fully complete. Make sure you create enough
   processes to handle your load.
2. Stop all pillows. You may have to be on above branch (for e.g. pillow-reorg)
```bash   
cchq <env> fab stop_pillows --branch=pillow-reorg
```
3. Run below django management command to create checkpoints for new pillows.
```bash   
cchq <env> django-manage create_checkpoints_for_merged_pillows
```
You can pass `--check` option to dry-run.
4. Deploy the change so that supervisor configuration is updated for the pillow switch.
```bash   
cchq <env> ap deploy_commcarehq.yml --tags=services --limit=pillowtop --branch=pillow-reorg
```
5. Run below command so that the supervisor process rereads the new config
```bash   
cchq <env> update-supervisor-confs --branch=pillow-reorg
```
6. Finally start all pillows.
```bash    
cchq <env> fab start_pillows --branch=pillow-reorg
```

You may do few checks to make sure the change is deployed succesfully.

1. Do a `sudo supervisorctl status all` on all pillow machines and make sure that new pillows are running succesfully and old pillows are not.
2. Look at pillow logs for new pillows and make sure there are no errors.
3. Do basic QA of various change feeds like
   - Submit few forms, and make sure they appear in the UCR and standard reports
   - Create few mobile workers and make sure they are searchable in report filters
4. Keep an eye on https://app.datadoghq.com/dash/256236/change-feeds-pillows

At this point if all goes well, the above PR can be merged.

If anything goes wrong beyond repair, the change can be rolled back, by following
the all of above steps can be repeated using master branch instead of 
your pillow-reorg branch (the third step can be skipped).
