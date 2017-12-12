//
// Toggles the visibility of the details of the build for the given commit.
//
function toggleBuildDetails(commit_id) {
	// Mark all build cells as cells with no showed details. Later, we mark
	// only the build cell for the commit of which we want to show the details.
	$("[id^=build-cell-]").removeClass('build-shown-details');

	// Toggle the case details.
	var buildDetails = $('#build-details-' + commit_id)
	if (buildDetails.is(':visible')) {
		buildDetails.hide();
	} else {
		// Hide the shown details of the builds for other commits (if any) and
		// show the build details only for the given commit.
		$("[id^=build-details-]").hide();
		// Mark the result cell as a cell with shown details.
		$("#build-cell-" + commit_id).addClass('build-shown-details');
		buildDetails.show();
	}
}

//
// Hides all the shown results and details for every case of every commit.
//
function hideCaseResultsAndDetails() {
	$("[id^=case-results-]").removeClass('case-results-shown-details');
	$("[id^=case-details-]").hide();
}

//
// Toggles the visibility of the details for the given module.
//
function toggleModuleDetails(module_id) {
	$('.module-details-' + module_id).toggle();
	if ($('.module-details-' + module_id).is(':visible')) {
		$('#module-results-' + module_id).addClass('module-results-row-shown');
	} else {
		$('#module-results-' + module_id).removeClass('module-results-row-shown');
	}

	// Hide the shown results and details to ensure that when module details
	// are hidden, no case details are left hanging.
	hideCaseResultsAndDetails();
}

//
// Toggles the visibility of the details for the given case.
//
function toggleCaseDetails(case_id) {
	var caseDetails = $('#case-details-' + case_id)
	if (caseDetails.is(':visible')) {
		// We can hide everything.
		hideCaseResultsAndDetails();
	} else {
		// Show only the given case details.
		hideCaseResultsAndDetails();
		$("#case-results-" + case_id).addClass('case-results-shown-details');
		caseDetails.show();
	}
}

//
// Shows the given tool arguments.
//
function showToolArgs(args, span) {
	alert(args);
}
