# Standard library
import inspect
import logging
import os.path

# First-party/Local
import ccos.log

log_name = os.path.basename(os.path.splitext(inspect.stack()[-1].filename)[0])
LOG = logging.getLogger(log_name)
ccos.log.reset_handler()


def map_repo_to_labels(repo, final_labels, non_destructive=True):
    """
    Map the given list of labels to GitHub. Any labels that do not already
    exist on the repository will be created and if chosen to, any additional
    lables on the repository will be removed.
    @param repo: the repo on which the labels are being synced
    @param final_labels: the list of labels that should be present on the repo
    @param non_destructive: whether to trim extra labels or preserve them
    """

    LOG.info("Fetching initial labels...")
    initial_labels = {
        label.name.casefold(): label for label in repo.get_labels()
    }
    LOG.log(ccos.log.SUCCESS, f"done. Found {len(initial_labels)} labels.")

    LOG.info("Parsing final labels...")
    final_labels = {
        label.qualified_name.casefold(): label for label in final_labels
    }
    LOG.log(ccos.log.SUCCESS, f"done. Found {len(final_labels)} labels.")

    if not non_destructive:
        LOG.info("Syncing initial labels...")
        ccos.log.change_indent(+1)
        for initial_label_name, initial_label in initial_labels.items():
            LOG.info(f"Syncing '{initial_label_name}'...")
            ccos.log.change_indent(+1)
            if initial_label_name not in final_labels:
                LOG.info("Does not exist, deleting...")
                initial_label.delete()
                LOG.log(ccos.log.SUCCESS, "done.")
            ccos.log.change_indent(-1)
            LOG.log(ccos.log.SUCCESS, "done.")
        ccos.log.change_indent(-1)
        LOG.log(ccos.log.SUCCESS, "done.")

    LOG.info("Syncing final labels...")
    ccos.log.change_indent(+1)
    for final_label_name, final_label in final_labels.items():
        LOG.info(f"Syncing '{final_label_name}'...")
        ccos.log.change_indent(+1)
        if final_label_name not in initial_labels:
            LOG.info("Did not exist, creating...")
            repo.create_label(**final_label.api_arguments)
            LOG.log(ccos.log.SUCCESS, "done.")
        elif final_label != initial_labels[final_label_name]:
            LOG.info("Differences found, updating...")
            initial_label = initial_labels[final_label_name]
            initial_label.edit(**final_label.api_arguments)
            LOG.log(ccos.log.SUCCESS, "done.")
        else:
            LOG.info("Match found, moving on.")
        ccos.log.change_indent(-1)
        LOG.log(ccos.log.SUCCESS, "done.")
    ccos.log.change_indent(-1)
    LOG.log(ccos.log.SUCCESS, "done.")


def set_labels(repos, standard_labels, repo_specific_labels):
    """
    Set labels on all repos for the organisation. This is the main entrypoint
    of the module.
    """

    for repo in list(repos):
        LOG.info(f"Getting labels for repo '{repo.name}'...")
        labels = standard_labels + repo_specific_labels.get(repo.name, [])
        LOG.log(ccos.log.SUCCESS, f"done. Found {len(labels)} labels.")
        LOG.info(f"Syncing labels for repo '{repo.name}'...")
        map_repo_to_labels(repo, labels)
        LOG.log(ccos.log.SUCCESS, "done.")


__all__ = ["set_labels"]
