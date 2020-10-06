# Workflow Design Document

Open to suggestions and PRs on any of this.

## Caching
For **analysis** workflows, the initial step is always doing some sort of quality control and data cleaning before the analytical steps.

Currently, the results of this are cached and can be reused in later analysis runs of the same samples as long as the parameters for the QC are the same.

### Goals
- allow developers to write their own QC steps
- allow developers to define a comparison for checking against existing caches
- result of QC steps needs to be sample files (FASTQ) that can be stored as a cache
- running FastQC on the data is compulsory and done automatically after QC steps
  - result must be stored in DB

## Analysis Steps

User defined units of work.

### Current State
- workflow and setup/teardown steps are mixed together
  - **clearly separate them**
- access to the filesystem is uncontrolled
  - **give developers their required files in the work environment and make developers upload files they want to keep for posterity**

### Goals
- provide easy way for developers to run external tools (currently `run_subprocess`)
- provide starting directory environment for steps
  - paths
    - `/references/`
      - reference data
      - currently use two variations on the reference
        - one built from 'default' isolates stored at `<data_path>/references/:id`
        - one built _ad hoc_ directly from the database based on OTU matches from an initial search against the above
        - find a way to provide a function for developers to derive `ad hoc` references without touching the database
    - `/subtractions/`
      - we will support multiple subtractions in future
      - provide paths to subtractions in environment
    - `/hmms/`
      - contains the profiles.hmm files used in NuVs
      - download profiles.hmm and run hmmbuild automatically
      - provide path that can be passed directly to hmmer
    - `/reads/`
      - provide each prepped read file for the sample
      - provide paths
    - `/upload`
      - compressed and uploaded to application storage
      - have developers set names for the uploaded files (eg. `upload("file.json", path)`)
      - maybe limit file formats supported for upload
  - this storage is ephemeral
    - should use `TemporaryDirectory` maybe; customize temporary path in `workflow execute`
    - all data to be kept must be explicitly uploaded by developer
  - job does not access filesystem outside temporary directory
  - keep in mind move to object storage will be made in near future
    - may try to support both storage paradigms for users that can't use object storage

### Misc
- cleanup can be automatic for all analysis jobs
  - delete analysis document
  - update job status
  - dispose of temporary directory
- should we have a special step the returns the `result` to be stored in the DB instead