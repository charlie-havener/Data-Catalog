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
