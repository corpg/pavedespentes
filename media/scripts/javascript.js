function show(id)
{
	document.getElementById(id).style.visibility='visible';
	document.getElementById(id).onMouseOut='hide('+id+')';
}

function hide(id)
{
	document.getElementById(id).style.visibility='hidden';
}
