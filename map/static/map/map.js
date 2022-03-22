// global variables

var mapCenter = [30.041394878798638,31.307350234985355]
var mymap = L.map('map').setView(mapCenter, 13);
var city_active_installation_ids = [];
var active_installation_ids= [];
var active_filters = [];
var active_category_filters = [];
var filters = JSON.parse(document.getElementById('filtersjs').textContent)


// Js for sidebar
function open_left_sidebar() {
	document.getElementById("left_sidebar").style.width = "220px";
	document.getElementById("main").style.marginLeft = "220px";
	document.getElementById("main").style.marginTop = "0px";
}

function close_left_sidebar() {
	document.getElementById("left_sidebar").style.width = "0px";
	document.getElementById("main").style.marginLeft = "0px";
}

// Js for sidebar
function open_right_sidebar() {
	document.getElementById("right_sidebar").style.width = "220px";
	document.getElementById("main").style.marginRight= "220px";
	document.getElementById("main").style.marginTop = "0px";
}

function close_right_sidebar() {
	document.getElementById("right_sidebar").style.width = "0px";
	document.getElementById("main").style.marginRight= "0px";
}

function toggleButton() {
	if (!this.isToggled) {
		openNav();
	} else {
		closeNav();
	}
	this.isToggled = !this.isToggled;
}

open_left_sidebar();
open_right_sidebar();


// Define different tileLayer for map ---

// mapbox layer
var mapbox = L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {
	attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
	maxZoom: 18,
	id: 'mapbox/streets-v11',
	tileSize: 512,
	zoomOffset: -1,
	accessToken: 'pk.eyJ1IjoibW9qaXJvc2kiLCJhIjoiY2t2czl3Y2VzMGE3eTJ2bzJhMXdiMGM4ciJ9.RArnejioh0AnjXVmZWP9-A'
});

// Google streets
var googleStreets = L.tileLayer('http://{s}.google.com/vt/lyrs=m&x={x}&y={y}&z={z}', {
	maxZoom: 20,
	subdomains: ['mt0', 'mt1', 'mt2', 'mt3']
});

// Google satellite
var googleSat = L.tileLayer('http://{s}.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', {
	maxZoom: 20,
	subdomains: ['mt0', 'mt1', 'mt2', 'mt3']
});


mapbox.addTo(mymap)
mapbox.setOpacity(40/100);


// figures

// functions to work with Json files on map for Figures
function onEachFeature(feature,layer) {
	//binds the pop up and tool tip to each feature
	//skips tooltips for districts because they '  ' the tooltip from other objects
	layer.bindPopup(feature.pop_up,{maxWidth:200,closeButton:false});
	if (!layer.feature.tool_tip.toLowerCase().includes('district')) {
	layer.bindTooltip(feature.tool_tip);
	}
}

function make_pop_up(figure) {
	//create a pop up based on the figure information
	[app_name,model_name] = figure.model.split('.')
	if (figure.fields.name.toLowerCase().includes('district')) {
	var m = '<p class="mt-0 mb-0">'+figure.fields.name+'</p>'
	}
	else {
	var m = '<p class="mt-2 mb-0">'+figure.fields.name+'</p>'
	// {#m += '<p class="mt-2 mb-0">'+figure.fields.description+'</p>'#}
	m += '<a class = "btn btn-link btn-sm mt-1 pl-0 text-dark" href='
	m += '/installations/figure/new/' + figure.pk
	m += ' role="button"><i class="far fa-edit"></i></a>'
	}
	return m
}

function add_popup_and_tooltip(data,pop_up,figure_name) {
	//set the pop up and tool tip on geojson features
	for (let i=0;i<data.features.length;i++){
		var feature = data.features[i]
		feature['pop_up'] = pop_up
		feature['tool_tip']= figure_name
	}
}

async function add_figure(figure) {
	//function loads the json figure connected to figure through ajax
	//fetches the correct style and creates a popup and tooltip
	const response = await fetch('/map/geojson_file/'+figure.fields.geojson)
	const data = await response.json()
	if (data.file == false || data.json == false) {return;}
	style = make_style(figure);
	var pop_up = make_pop_up(figure);
	add_popup_and_tooltip(data,pop_up,figure.fields.name)
	// {#L.geoJSON(data).addTo(mymap)#}
	var geosjson_layer = L.geoJSON(data,{style:style,onEachFeature:onEachFeature})
	Landlayers.push({'figure':figure,'layer':geosjson_layer,'style':style})
}

// neighbourhoods

function turnoff_neighbourhoods() {
    for (let i = 0;  i < Neighbourlayers.length;i++) {
        var n = Neighbourlayers[i];
        n.layer.setStyle({fillOpacity:0.0});
    }
}

function highlight_neighbourhood(name) {
    turnoff_neighbourhoods();
    for (let i = 0;  i < Neighbourlayers.length;i++) {
        var n = Neighbourlayers[i];
        if (n.neighbourhood.fields.name == name) {
            n.layer.setStyle({fillOpacity:0.5});
        }
    }
}

async function get_neighbourhood(installation_identifier) {
	//heighlights neighbourhood on installation hover
    const response=await fetch('/map/get_neighbourhood/'+installation_identifier)
    const data = await response.json()
    names = data['neighbourhoods']
    for (let i = 0;  i < names.length;i++) {
        var name = names[i];
        highlight_neighbourhood(name);
    }
}

async function add_neighbourhood(neighbourhood) {
	//function loads the json figure connected to figure through ajax
	//fetches the correct style and creates a popup and tooltip
	var path = neighbourhood.fields.extent_shapefile
	const response = await fetch('/map/geojson_file/'+path)
	// const response = await fetch('/media/'+neighbourhood.fields.extent_shapefile)
	const data = await response.json()
	if (neighbourhood.fields.style == null){
		var style = {
		"color": "#6BA884",
		"weight": 3,
		"opacity": 0.8,
		"fillOpacity": 0,
		"z_index": 0
		};
		style ={...style,...{"dashArray": '20, 20'}}
	}
	else{
		style = make_style(neighbourhood);
	}
	var pop_up = make_pop_up_neighbour(neighbourhood);
	var tooltip_str = 'Neighbourhood '
	tooltip_str += neighbourhood.fields.neighbourhood_number.toString();
	add_popup_and_tooltip(data,pop_up,tooltip_str)
	// {#L.geoJSON(data).addTo(mymap)#}
	var geosjson_layer = L.geoJSON(data,
		{style:style,onEachFeature:onEachFeature_neighbour})
	Neighbourlayers.push({'neighbourhood':neighbourhood,
		'layer':geosjson_layer,'style':style})
}

// functions to work with Json files of Neighbourhoods
function onEachFeature_neighbour(feature,layer) {
	//binds the pop up and tool tip to each feature
	//skips tooltips for districts because they '  ' the tooltip from other objects
	layer.bindPopup(feature.pop_up,{maxWidth:200,closeButton:false});
	layer.bindTooltip(feature.tool_tip);
}

function make_pop_up_neighbour(neighbourhood) {
	//create a pop up based on the neighbourhood information
	[app_name,model_name] = neighbourhood.model.split('.')
	var m = '<p class="mt-0 mb-0">'+'Neighbourhood '
	m += neighbourhood.fields.neighbourhood_number+'</p>'
	m += '<a class = "btn btn-link btn-sm mt-1 pl-0 text-dark" href='
	m += '/installations/neighbourhood/new/' + neighbourhood.pk
	m += ' role="button"><i class="far fa-edit"></i></a>'
	return m
}


function show_layers_neighbour(){
	for (i = 0; i<Neighbourlayers.length; i++) {
		layer = Neighbourlayers[i];
		mymap.addLayer(layer.layer);
	}
}

async function check_done_loading_neighbour(list,expected_n) {
	//check whether the expected_n number of values are loaded into the array list
	while (true) {
		await new Promise(r => setTimeout(r,100));
		if (list.length == expected_n) {break;}
	}
	show_layers_neighbour();
}


// add Neighbourhoods------------------------
var Neighbourlayers = [];
neighbourhoods = JSON.parse(document.getElementById('neighbourhoodsjs').textContent)

for (i = 0; i<neighbourhoods.length; i++) {
	//create figures to plot on the leaflet map
	add_neighbourhood(neighbourhoods[i]);
}

check_done_loading_neighbour(Neighbourlayers,neighbourhoods.length);

//city CITY

function turnoff_cities() {
    var cities = document.getElementsByClassName('city-link')
     for (let i = 0;  i < cities.length;i++) {
        var city = cities[i];
        city.style.color = 'lightgrey';
    }
}

function highlight_city(name) {
    turnoff_cities();
    var e = document.getElementById(name);
    e.style.color = 'black';
}

// set map to city
function setMapCenter(chosen) {
	console.log('set map center',chosen)
    var e = document.getElementById(chosen);
    city_active_installation_ids = e.getAttribute('data_installation_ids').split(',');
    active_installation_ids = e.getAttribute('data_installation_ids').split(',');
	cityjs = JSON.parse(document.getElementById('cjsjs').textContent)
	for (i = 0; i<cityjs.length; i++) {
	//Check which city is selected
		if (cityjs[i].fields.name === chosen){
			mapCenter = [cityjs[i].fields.latitude, cityjs[i].fields.longitude];
			mymap.setView(mapCenter, 12);
		}
	}
    highlight_city(chosen);
    city = chosen;
    hide_show_elements();
	//update_filters_after_city_change();
	// was hard to get it to work with changing visible filters.
	active_filters = [];
	active_category_filters = [];
}

// style

function get_style(pk) {
	//style is a foreign key on the figure object, 
	//this function returns the correct style based on the pk
	for (i = 0; i<styles.length; i++) {
		if (styles[i].pk === pk) {return styles[i]}
	}
	return '#CCFFAA'
}

function make_style(figure){
	//create a dict that sets the style of a figure 
	//(based on the style objects in the database
	style= get_style(figure.fields.style);
	var myStyle = {
		"color": style.fields.color,
		"weight": style.fields.stroke_weight,
		"opacity": style.fields.stroke_opacity,
		"fillOpacity": style.fields.fill_opacity,
		"z_index": style.fields.z_index
	};
	if (style.fields.dashed) {myStyle ={...myStyle,...{"dashArray": '20, 20'}}}
	return myStyle
}


function show_layers(){
	//show the figures in the order of the z index
	Landlayers.sort((a,b) => a.style.z_index - b.style.z_index)
	for (i = 0; i<Landlayers.length; i++) {
		layer = Landlayers[i];
		//check whether a figure overlaps with the current time range 
		//and only plot those that do
		overlap = check_overlap(layer.figure.fields.start_date, 
			layer.figure.fields.end_date)
		if (overlap) {mymap.addLayer(layer.layer);}
		else {mymap.removeLayer(layer.layer);}
	}
}

async function check_done_loading(list,expected_n) {
	//check whether the expected_n number of values are loaded into the array list
	while (true) {
		await new Promise(r => setTimeout(r,100));
		if (list.length == expected_n) {break;}
	}
	show_layers();
}

//------------------------------------
//add Figures-------------------------------
var Landlayers = [];
styles = JSON.parse(document.getElementById('stylesjs').textContent)
figures = JSON.parse(document.getElementById('figuresjs').textContent)

for (i = 0; i<figures.length; i++) {
	//create figures to plot on the leaflet map
	add_figure(figures[i]);
}

check_done_loading(Landlayers,figures.length);
//-----------------------------------------

// date slider
// Multi slider for Date range
var start = 500;
var end = 1200;
var multi_slider = document.getElementById('years');
noUiSlider.create(multi_slider, {
	start: [start, end],
	connect: true,
	range: {'min':300,'max':1500},
	steps: 50,
	tooltips: true,
	format: {to: function (value) {return Math.floor(value)},
		from: function (value) {return Math.floor(value)}},
});


function check_overlap(low,high){
	//compare start and end date of a figure with start end date of the year slider
	if (low <= start && high >= start){ return true;}
	if (low >= start && high <= end){ return true;}
	if (low <= end && high >= start){ return true;}
	return false;
}

multi_slider.noUiSlider.on('change',handleYearSlider);

function handleYearSlider(values) {
	//set start and end values based on the year slider, 
	//this is used to determine which
	//figures are shown
	start= values[0];
	end= values[1];
	// console.log(values)
	show_layers();
}
//----------------------------------------
//create slider to control opacity of the map tiles
var slider = document.getElementById('map_opacity');
noUiSlider.create(slider, {
	start: [40],
	range: {'min':0,'max':100},
	steps: 1,
});

slider.noUiSlider.on('slide',function(value){
	// set all base maps opacity
	mapbox.setOpacity(value/100);
	googleStreets.setOpacity(value/100);
	googleSat.setOpacity(value/100);
});
//-----------------------
// Layer controller
var baseMaps = {
   "MapBox": mapbox,
   "Google streets": googleStreets,
   "Google satellite": googleSat,
};

var overlayMaps = {
};

L.control.layers(baseMaps, overlayMaps).addTo(mymap);

//-----------------------


//-----------------------
// installations show hide

function get_all_installation_ids() {
    var installations = document.getElementsByClassName('installation-title');
    var installation_ids = [];
    for (i = 0; i < installations.length; i ++) {
        var installation = installations[i]
        installation_ids.push(installation.id);
    }
    return installation_ids
}

function hide_show_elements(update_counts = true) {
    _update_installations(update_counts);
}

function _update_installations(update_counts = true) {
	//shows or hides installations based on filters /city / date range (WIP)
    for (let i= 0;i< installation_ids.length;i++) {
        var identifier = installation_ids[i];
        installation = document.getElementById(identifier+'-item');
        if (active_installation_ids.includes(identifier)) {
            installation.style.display = '';
        } else {
            installation.style.display = "none";
        }
    }
	if (update_counts) {
		update_filter_counts();
	}
}

function count_active_installation_ids(installation_ids) {
	//count the number of installations that are currently active of the
	// list installtion ids provides
	count = 0;
    for (let i= 0;i< installation_ids.length;i++) {
        var identifier= installation_ids[i];
		if ( active_installation_ids.includes(identifier) ) {
			count ++
		}
	}
	return count
}

// FILTERS filters filter filtering

function update_filters_after_city_change() {
	var temp = [...active_filters];
	for (i = 0; i<temp.length; i++) {
		filter_id = temp[i]
		var filter = document.getElementById(filter_id);
		if ( !Boolean(filter) ) { continue; }
		var index = active_filters.indexOf(filter_id)
		active_filters.splice(index,1)
		if ( filter.style.display == 'none' ) { continue}
		toggle_filter(filter_id)
	}
	var temp = [...active_category_filters];
	for (i = 0; i<temp.length; i++) {
		category_filter_id = temp[i]
		var category_filter = document.getElementById(category_filter_id);
		if ( !Boolean(category_filter) ) { continue; }
		var index = active_category_filters.indexOf(filter_id)
		active_category_filters.splice(index,1)
		if ( category_filter.style.display == 'none' ) { continue}
		toggle_category_filter(category_filter_id);	
	}
	update_filters();
}

function update_filter_counts() {
	//displays the number of instances for each filter and category there are
	//hides filters if the count == 0
	var filters = document.getElementsByClassName('filter-count');
    for (let i= 0;i< filters.length;i++) {
        var filter = filters[i];
		//console.log(filter);
		var installation_ids = filter.getAttribute('data_installation_ids').split(',');
		var count = count_active_installation_ids(installation_ids);
		if ( count == 0 ) {
			filter.style.display = "none";
		 	if ( [...filter.classList].includes('watersystemcategory') ) {
				var div= document.getElementById(filter.id + '-all');
				div.style.display = "none";
			}
		} else {
			filter.style.display = "";
			var html =filter.innerHTML.split('(')[0] + '(' + count + ') </small>';
			filter.innerHTML= html;
		 	if ( [...filter.classList].includes('watersystemcategory') ) {
				var div = document.getElementById(filter.id + '-all');
				div.style.display = "";
			}
		}
	}
}

function update_active_installation_ids(installation_ids, action) {
	for (let i= 0; i < installation_ids.length; i++) {
		var installation_id = installation_ids[i];
		if ( action == 'add' && city_active_installation_ids.includes(installation_id) ) {
			if ( !active_installation_ids.includes(installation_id) )
				active_installation_ids.push(installation_id);
		}
		else if ( action == 'remove' && active_installation_ids.includes(installation_id) ) {
			var index = active_installation_ids.indexOf(installation_id);
			active_installation_ids.splice(index,1);
		}
	}
}

function check_category_filter_active(filter) {
    var installation_ids= filter.getAttribute('data_installation_ids').split(',');
	active = false;
	for (let i= 0; i < installation_ids.length; i++) {
		var installation_id = installation_ids[i];
		if ( active_installation_ids.includes(installation_id) ) {
			active = true;
			break;
		}
	}
	return active
}

function update_filters() {
	var filters = document.getElementsByClassName('filter-count');
	var selected = '#818181'
	var unselected = '#bfbdbd'
	for (let i= 0; i < filters.length; i++) {
		var filter = filters[i];
		if ( filter.classList.contains('watersystemcategory') ) {
			if ( check_category_filter_active(filter) ) {
				filter.style.color = selected;
			} else {
				filter.style.color = unselected;
			}
		}
		else if ( active_filters.includes(filter.id) || active_filters.length == 0) {
			filter.style.color = selected;
		} else {
			filter.style.color = unselected;
		}
	}
}

function toggle_filter(filter_id) {
	// toggles a filter on or off
	var filter = document.getElementById(filter_id);
    //var installation_ids= filter.getAttribute('data_installation_ids').split(',');
	var filter_info = filters.filter_dict[filter_id]
	var installation_ids = filter_info.installation_ids
	var action = 'add';
	if ( active_filters.includes(filter_id) ) { 
		//removing a filter
		action = 'remove'; 
		var index = active_filters.indexOf(filter_id) 
		active_filters.splice(index,1);
		filter_info.active = false;
	} else {
		// adding a filter
		if (active_filters.length == 0) {
			// no filters are active, only show instances related to this filter
			active_installation_ids = [];	
		}
		active_filters.push(filter_id);
		filter_info.active = true;
	}
	if (active_filters.length == 0) { 
		//no more filters active, showing all installation of the city
		active_installation_ids = city_active_installation_ids; 
	} else {
		update_active_installation_ids(installation_ids,action);
	}
	hide_show_elements(update_counts= false);
	update_filters();
	if ( active_installation_ids.length == city_active_installation_ids.length ) {
		active_filters = [];
		active_category_filters = [];
	}
} 

function check_category_filter_status(filter_ids) {
	var count = 0;
	var visible_filters = 0;
	var category_filter_status = '';
	var check = [];
	for (let i= 0; i < filter_ids.length; i++) {
		var filter_id = filter_ids[i];
		var filter = document.getElementById(filter_id);
		if (!Boolean(filter)) {continue;}
		if (filter.style.display == '') { visible_filters ++; check.push(filter.id)}
		if ( active_filters.includes(filter_id) ) {count ++; check.push(filter_id)}
	}
	if ( count == 0 ) { category_filter_status = 'inactivate' }
	else if ( count == visible_filters ) { category_filter_status = 'complete'; }
	else {category_filter_status = 'partitial';}
	return category_filter_status
}

function toggle_category_filter(category_filter_id) {
	var category_filter = document.getElementById(category_filter_id);
	var category_filter_info = filters.category_filter_dict[category_filter_id]
    //var filter_ids= category_filter.getAttribute('data_filter_ids').split(',');
    var filter_ids= Object.keys(category_filter_info.filter_dict)
	category_filter_status = check_category_filter_status(filter_ids);
	if ( active_category_filters.includes(category_filter_id) && 
			category_filter_status == 'complete') { 
		for (let i= 0; i < filter_ids.length; i++) {
			var filter_id = filter_ids[i];
			if ( active_filters.includes(filter_id) ) {
				toggle_filter(filter_id);	
			}
		}
		var index = active_category_filters.indexOf(category_filter_id) 
		active_category_filters.splice(index,1);
	} else {
		for (let i= 0; i < filter_ids.length; i++) {
			var filter_id = filter_ids[i];
			if ( !active_filters.includes(filter_id) ) {
				var filter = document.getElementById(filter_id);
				if (!Boolean(filter) || filter.style.display == 'none') {continue;}
				toggle_filter(filter_id);	
			}
		}
		active_category_filters.push(category_filter_id);
	}
}


var city = JSON.parse(document.getElementById('cityjs').textContent)
// heighlight_city(city);
var installation_ids = get_all_installation_ids();
// document.addEventListener('DOMContentLoaded',highlight_city(city))
setMapCenter(city);

