// global variables

var mapCenter = [30.041394878798638,31.307350234985355]
var mymap = L.map('map').setView(mapCenter, 13);
var city_active_installation_ids = [];
var active_installation_ids= [];
var date_exclude_installation_ids = [];
var active_filters = [];
var active_category_filters = [];
var filters = JSON.parse(document.getElementById('filtersjs').textContent)
var highlighted_installations = [];
var highlighted_neighbourhood_layer= null;
var neighbourhood_activate_installation_ids = []
var neighbourhood_layers_clicked = []

var neighbourhood_style = {"color": "#9AD076","weight": 3,"opacity": 0.8,
	"fillOpacity": 0,"z_index": 0};
neighbourhood_style ={...neighbourhood_style,...{"dashArray": '20, 20'}}
neighbourhood_color = null;


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
	var m = '<p class="mt-2 mb-0">'+figure.name+'</p>'
	m += '<a class = "btn btn-link btn-sm mt-1 pl-0 text-dark" href='
	m += '/installations/figure/new/' + figure.pk
	m += ' role="button"><i class="far fa-edit"></i></a>'
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
	const response = await fetch('/map/geojson_file/'+figure.geojson)
	const data = await response.json()
	if (data.file == false || data.json == false) {return;}
	style = make_style(figure);
	var pop_up = make_pop_up(figure);
	add_popup_and_tooltip(data,pop_up,figure.name)
	// {#L.geoJSON(data).addTo(mymap)#}
	var geosjson_layer = L.geoJSON(data,{style:style,onEachFeature:onEachFeature})
	figure_layers.push({'figure':figure,'layer':geosjson_layer,'style':style})
}

// neighbourhoods

function turnoff_neighbourhoods() {
	// turns of highlight (created by hovering over an installation in the right sidebar)
    for (let i = 0;  i < Neighbourlayers.length;i++) {
        var n = Neighbourlayers[i];
		if (n == highlighted_neighbourhood_layer) {continue}
        n.layer.setStyle({fillOpacity:0.0});
    }
}

function highlight_neighbourhood(pk) {
	// highlights a neighbourhood (by hovering over an installation in the right sidebar)
    for (let i = 0;  i < Neighbourlayers.length;i++) {
        var n = Neighbourlayers[i];
		if (n == highlighted_neighbourhood_layer) {continue}
        if (n.neighbourhood.pk == pk) {
            n.layer.setStyle({fillOpacity:0.3});
        }
    }
}

function turnon_neighbourhood(data) {
	//highlights neighbourhood on installation hover
    // turnoff_neighbourhoods();
    var d = data['neighbourhoods']
    for (let i = 0;  i < d.length;i++) {
        var pk = d[i].pk;
        highlight_neighbourhood(pk);
    }
}

function find_neighbourhood(leaflet_id) {
	// find neighbourhood_layer based on leaflet element (provided by onhover onclick)
	// the neighbourhood_layer and leaflet element are apperently distinct things
    for (let i = 0;  i < Neighbourlayers.length;i++) {
        var n = Neighbourlayers[i];
		if (n.layer._leaflet_id == leaflet_id) { return n;}
	}
	return null
}

function highlight_installations_on_hover(installation_ids) {
	// highlights installation on neighbourhood hover
	if (!installation_ids) {return}
    for (let i = 0;  i < installation_ids.length;i++) {
		var installation_id = installation_ids[i];
		var installation = document.getElementById(installation_id);
		installation.classList.add('installation-highlight')
		highlighted_installations.push(installation);
	}

}

function turnoff_installations() {
	// turn of previously highlighted installations (on neighbourhood hover) in the list
    for (let i = 0;  i < highlighted_installations.length;i++) {
		var installation= highlighted_installations[i];
		installation.classList.remove('installation-highlight')
	}
	highlighted_installations = []
}

function turnoff_previously_hovered_neighbourhood() {
	// turns of highlight of previously hover neighbourhood
	if (highlighted_neighbourhood_layer) {
		// turn of previously highlighted neighbourhood
		if (neighbourhood_layers_clicked.includes(highlighted_neighbourhood_layer)) {
			// if the neighbourhood is clicked 'on' set it to clicked status
			var s = {color: '#769dd0',fillOpacity:0.6};
			highlighted_neighbourhood_layer.layer.setStyle(s);
		} else {
			highlighted_neighbourhood_layer.layer.setStyle({fillOpacity:0.0});
		}
	}
}

function highlight_neighbourhood_on_hover(ev) {
	// highlights neighbourhood when hovered over 
	// highlights linked installations in the right sidebar
	turnoff_previously_hovered_neighbourhood(); 
	turnoff_installations(); // turn of previously highlighted installations
	var neighbourhood_layer = find_neighbourhood(ev.target._leaflet_id)
	highlighted_neighbourhood_layer = neighbourhood_layer;
	var installation_ids = neighbourhood_layer.neighbourhood.installation_ids
	if (installation_ids) {
		highlight_installations_on_hover(installation_ids)
		highlighted_neighbourhood_layer.layer.setStyle({fillOpacity:0.6})
	} else {
		highlighted_neighbourhood_layer.layer.setStyle({fillOpacity:0.1})
	}
	
} 

function _set_neighbourhood_active_installations() {
	// udpate the neighbourhood_activate_installation_ids with installation linked to
	// the neighbourhoods in the neighbourhood_layers_clicked array
	// helper function of toggle_neighbourhood_on_click
	neighbourhood_activate_installation_ids = [];
	for (let i = 0;i < neighbourhood_layers_clicked.length;i++) {
		// loop over neighbourhood_layers in the clicked array
		var neighbourhood_layer = neighbourhood_layers_clicked[i]
		var installation_ids = neighbourhood_layer.neighbourhood.installation_ids
		for (let j = 0;  j < installation_ids.length;j++) {
			//loop over the installation_ids linked to a given neighbourhood
			var installation_id = installation_ids[j];
			if (!neighbourhood_activate_installation_ids.includes(installation_id)) {
				index=neighbourhood_activate_installation_ids.indexOf(installation_id)
				neighbourhood_activate_installation_ids.push(installation_id);
			}
		}
	}
}

function toggle_neighbourhood_on_click(ev) {
	// activates / inactivates a neighbourhood, changes color of neighbourhood
	// adds linked installation_ids to the neighbourhood_activate_installation_ids
	// filters the installations shown in the right sidebar
	var neighbourhood_layer = find_neighbourhood(ev.target._leaflet_id)
	var installation_ids = neighbourhood_layer.neighbourhood.installation_ids
	if (!installation_ids) { return }
	if (neighbourhood_layers_clicked.includes(neighbourhood_layer) ) {
		var index = neighbourhood_layers_clicked.indexOf(neighbourhood_layer);
		neighbourhood_layers_clicked.splice(index,1)
		neighbourhood_layer.layer.setStyle({color: neighbourhood_color,fillOpacity:0.0});
		_set_neighbourhood_active_installations()
	} else {
		neighbourhood_layer.layer.setStyle({color: '#769dd0',fillOpacity:0.6});
		neighbourhood_layers_clicked.push(neighbourhood_layer);
		_set_neighbourhood_active_installations()
	}
	hide_show_elements()
}

async function add_neighbourhood(neighbourhood) {
	//function loads the json figure connected to figure through ajax
	//fetches the correct style and creates a popup and tooltip
	var path = neighbourhood.geojson
	const response = await fetch('/map/geojson_file/'+path)
	const data = await response.json()
	if (neighbourhood.style == null){ style = neighbourhood_style; }  
	else {style = make_style(neighbourhood);}
	var pop_up = make_pop_up(neighbourhood);
	var tooltip_str = 'Neighbourhood '
	tooltip_str += neighbourhood.number.toString();
	// add_popup_and_tooltip(data,pop_up,tooltip_str)
	var geosjson_layer = L.geoJSON(data,{style:style})
	geosjson_layer.on('mouseover',highlight_neighbourhood_on_hover)
	geosjson_layer.on('click',toggle_neighbourhood_on_click)
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
	m += neighbourhood.number+'</p>'
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
	neighbourhood_color = Neighbourlayers[0].style.color
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
	active_filters = [];
	active_category_filters = [];
	date_filter_installations();
	update_filters();
    //hide_show_elements();
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
	var style= get_style(figure.style);
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

function check_installation_id(figure) {
	//checks whether a figure should be shown based on possible linked installations
	if (!figure.installation_ids) 
		// if no installation are linked, show status = true, could be removed
		// based on the date filter
		{ return true } 
	for (let i = 0; i< figure.installation_ids.length; i ++) {
		installation_id = figure.installation_ids[i]
		if ( active_installation_ids.includes(installation_id) ) {
			// if a linked installation_id is active show the figure
			return true
		}
	}
	// if it is linked to installation_ids and none are currently active, 
	//do not show figure
	return false
}

function show_layers(){
	//show the figures in the order of the z index
	figure_layers.sort((a,b) => a.style.z_index - b.style.z_index)
	for (let i = 0; i<figure_layers.length; i++) {
		layer = figure_layers[i];
		//check whether a figure overlaps with the current time range 
		//and only plot those that do
		overlap = check_overlap(layer.figure.map_start_date, 
			layer.figure.map_end_date)
		show = check_installation_id(layer.figure)
		if (overlap && show) {mymap.addLayer(layer.layer)}
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
var figure_layers= [];
styles = JSON.parse(document.getElementById('stylesjs').textContent)
figures = JSON.parse(document.getElementById('figuresjs').textContent)

for (i = 0; i<figures.length; i++) {
	//create figures to plot on the leaflet map
	add_figure(figures[i]);
}

check_done_loading(figure_layers,figures.length);
//-----------------------------------------

// date slider
// Multi slider for Date range
var date_range = JSON.parse(document.getElementById('date_rangejs').textContent)
var start = date_range['earliest_date'];
var end = date_range['latest_date'];
var multi_slider = document.getElementById('years');
noUiSlider.create(multi_slider, {
	start: [start, end],
	connect: true,
	range: {'min':date_range['earliest_date'],'max':date_range['latest_date']},
	steps: 50,
	tooltips: true,
	format: {to: function (value) {return Math.floor(value)},
		from: function (value) {return Math.floor(value)}},
});


function check_overlap(low,high){
	//compare start and end date of a figure with start end date of the year slider
	if (!low) { return false;} //figure should always have start date to be visible
	if (!high) { // if end dat is not available check whether start date is after start
		if (low >= start && low <= end) { return true;}
		return false
	}
	if (low <= start && high >= start){ return true;}
	if (low >= start && high <= end){ return true;}
	if (low <= end && high >= start){ return true;}
	return false;
}

function date_filter_installations() {
	// updates a list of installations ids that are outside the range of the date slider
	// updates the displayed installations and the counts
	for (i = 0; i< city_active_installation_ids.length; i++) {
		installation_id = city_active_installation_ids[i];
		installation = document.getElementById(installation_id)
		if (!installation) { continue;}
		var low = parseInt(installation.getAttribute('data_map_start_date'))
		var high = parseInt(installation.getAttribute('data_map_end_date'))
		var overlap = check_overlap(low,high);
		if ( overlap ) {
			if (date_exclude_installation_ids.includes(installation_id) ) { 
				var index = date_exclude_installation_ids.indexOf(installation_id);
				date_exclude_installation_ids.splice(index,1);
			}
		} else { 
			if (!date_exclude_installation_ids.includes(installation_id) ) {
				date_exclude_installation_ids.push(installation_id); 
			}	
		}
	}
	hide_show_elements();
}

multi_slider.noUiSlider.on('change',handleYearSlider);

function handleYearSlider(values) {
	//set start and end values based on the year slider, 
	//this is used to determine which
	//figures are shown
	start= values[0];
	end= values[1];
	show_layers();
	date_filter_installations();
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
		if (neighbourhood_activate_installation_ids.length > 0) {
			// if any neighbourhood is clicked, also check whether the id 
			// is part of neighbourhood_activate_installation_ids array
			if (active_installation_ids.includes(identifier) 
				&& neighbourhood_activate_installation_ids.includes(identifier)
				&& !date_exclude_installation_ids.includes(identifier) ) {
				installation.style.display = '';
			} else {
				installation.style.display = "none";
			}
		}
        else if (active_installation_ids.includes(identifier) 
			&& !date_exclude_installation_ids.includes(identifier) ) {
			// if no neighbourhood is clicked only check active array and date exclusion
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
		if (neighbourhood_activate_installation_ids.length > 0) {
			// if a neighbourhood is clicked also take into account the 
			// neighbourhood_activate_installation_ids array
			if ( city_active_installation_ids.includes(identifier) 
				&& neighbourhood_activate_installation_ids.includes(identifier)
				&& !date_exclude_installation_ids.includes(identifier) ) {
				count ++
			}
		}
		else if ( city_active_installation_ids.includes(identifier) 
			&& !date_exclude_installation_ids.includes(identifier) ) {
			// if no neighbourhood is clicked
			// only take into account active ids and data exclusion
			count ++
		}
	}
	return count
}

// FILTERS filters filter filtering


function update_filter_counts() {
	//displays the number of instances for each filter and category there are
	//hides filters if the count == 0
	var filters = document.getElementsByClassName('filter-count');
    for (let i= 0;i< filters.length;i++) {
        var filter = filters[i];
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
		if ( action == 'add' && city_active_installation_ids.includes(installation_id)){
			if ( !active_installation_ids.includes(installation_id) )
				active_installation_ids.push(installation_id);
		}
		else if (action=='remove' && active_installation_ids.includes(installation_id)){
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
	show_layers(); // updates figures on the map
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

function turnoff_figure() {
    for (let i = 0;  i < figure_layers.length;i++) {
        var figure_layer = figure_layers[i];
        figure_layer.layer.setStyle({color: figure_layer.style.color,
			weight: figure_layer.style.weight});
    }
}

function highlight_figure(figure) {
    for (let i = 0;  i < figure_layers.length;i++) {
        var figure_layer = figure_layers[i];
        if (figure_layer.figure.pk == figure.pk) {
            figure_layer.layer.setStyle({color: '#f01d94',
            	weight: figure_layer.style.weight *2});
        }
    }
}

function turnon_figure(data) {
	//highlights figure on installation hover
    var figure = data['figure']
	if (figure) { highlight_figure(figure) }
}


async function turnon_map_repr(installation_identifier) {
    const response=await fetch('/map/get_map_representation/'+installation_identifier)
    const data = await response.json()
	turnoff_previously_hovered_neighbourhood(); //turn of neighbourhood hover highlights
	turnoff_installations(); //turn of neighbourhood hover highlights

	turnon_neighbourhood(data);
	turnon_figure(data)
}

function turnoff_map_repr() {
	turnoff_neighbourhoods();
	turnoff_figure();
}

var city = JSON.parse(document.getElementById('cityjs').textContent)
var installation_ids = get_all_installation_ids();
setMapCenter(city);

