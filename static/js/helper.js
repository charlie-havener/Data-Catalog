function editDescPopUp(clicked_id, editable_name, current_desc) {
	console.log(current_desc)
	Swal.fire({
		titleText: 'Update Description',
		text:'Enter an updated description for `' + editable_name + '`',
		input: 'text',
		inputValue: current_desc,
		confirmButtonColor: '#47c0e0',
		confirmButtonText: 'Update',
		width: '80%',
		showCancelButton: 'true',
		allowOutsideClick: 'false',
		allowEscapeKey: 'false',
	}).then((result) => {
		if (result.isConfirmed) {
			// this element is hidden, but the value is included with the htmx put request
			document.getElementById('updated-desc').value = result.value
			htmx.trigger('#'+clicked_id, 'confirmed')
		}
	})
}

function validateNewObjectForm() {
	console.log("submitted");
	let valid = true;

	let valid_classes = [
		"bg-gray-50",
		"border",
		"border-gray-300",
		"text-gray-900",
		"text-sm",
		"rounded-lg",
		"focus-visible:outline",
		"focus-visible:outline-blue-500",
		"focus:border-blue-500",
		"block",
		"w-full",
		"p-2.5",
	];
	let invalid_classes = [
		"bg-red-50",
		"border",
		"border-red-500",
		"text-red-900",
		"placeholder-red-700",
		"text-sm",
		"rounded-lg",
		"focus-visible:outline",
		"focus-visible:outline-red-500",
		"focus:border-red-500",
		"block",
		"w-full",
		"p-2.5",
	];

	// only name and type are requried
	let object_name = document.getElementById("object-name");
	object_name.classList.remove(...object_name.classList);
	if (object_name.value == "") {
		valid = false
		object_name.classList.add(...invalid_classes);
	}
	else {
		object_name.classList.add(...valid_classes);
	}

	let object_type = document.getElementById("object-type");
	object_type.classList.remove(...object_type.classList);
	if (object_type.value == "") {
		valid = false
		object_type.classList.add(...invalid_classes);
	}
	else {
		object_type.classList.add(...valid_classes);
	}

	if (valid) {
		console.log("valid form")
		htmx.trigger('#new-object-form', 'confirmed');
	} else {
		console.log("invalid form");
	}
}

function updateTabs(e) {
	// hide all of the data then mark the current tab as not hidden
	var tabData = document.getElementById("object-details-tabs-data");
	var associatedDataTab = e.getAttribute("data-tabs-target");
	for (c of tabData.children) {
		c.classList.add("hidden");
	}
	document.getElementById(associatedDataTab).classList.remove("hidden")

	// update the active button
	var t = document.getElementById("object-details-tabs-buttons");
	var tab_inactive_classes = t.getAttribute("data-tabs-inactive-classes").split(/\s+/);
	var tab_active_classes = t.getAttribute("data-tabs-active-classes").split(/\s+/);

	var tab_buttons = document.querySelector("#object-details-tabs-buttons").querySelectorAll("li > button");
	for (b of tab_buttons) {
		for (ac of tab_active_classes) {
			b.classList.remove(ac);
		}
		for (ic of tab_inactive_classes) {
			b.classList.add(ic);
		}
	}
	for (ac of tab_active_classes) {
		e.classList.add(ac);
	}
}
