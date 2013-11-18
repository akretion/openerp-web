/*---------------------------------------------------------
 * OpenERP web_graph
 *---------------------------------------------------------*/

/* jshint undef: false  */


openerp.web_graph = function (instance) {
'use strict';

var _lt = instance.web._lt;
var _t = instance.web._t;
var QWeb = instance.web.qweb;

instance.web.views.add('graph', 'instance.web_graph.GraphView');

 /**
  * GraphView view.  It mostly contains a widget (PivotTable), some data, and 
  * calls to charts function.
  */
instance.web_graph.GraphView = instance.web.View.extend({
    template: 'GraphView',
    display_name: _lt('Graph'),
    view_type: 'graph',
    mode: 'pivot',   // pivot, bar_chart, line_chart or pie_chart
    pivot_table: null,

    events: {
        'click .graph_mode_selection li' : function (event) {
            event.preventDefault();
            this.mode = event.target.attributes['data-mode'].nodeValue;
            this.display_data();
        },
    },

    view_loading: function (fields_view_get) {
        var self = this;
        var model = new instance.web.Model(fields_view_get.model, {group_by_no_leaf: true});
        var domain = [];
        var col_groupby = [];
        var row_groupby = [];
        var measure = null;
        var fields;
        var important_fields = [];

        // get the default groupbys and measure defined in the field view
        _.each(fields_view_get.arch.children, function (field) {
            if ('name' in field.attrs) {
                if ('operator' in field.attrs) {
                    measure = field.attrs.name;
                } else {
                    row_groupby.push(field.attrs.name);
                }
            }
        });

        // get the most important fields (of the model) by looking at the
        // groupby filters defined in the search view
        var load_view = instance.web.fields_view_get({
            model: model,
            view_type: 'search',
        });

        var important_fields_def = $.when(load_view).then(function (search_view) {
            var groups = _.select(search_view.arch.children, function (c) {
                return (c.tag == 'group') && (c.attrs.string != 'Display');
            });
            _.each(groups, function(g) {
                _.each(g.children, function (g) {
                    if (g.attrs.context) {
                        var field_id = py.eval(g.attrs.context).group_by;
                        important_fields.push(field_id);
                    }
                });
            });
        });

        // get the fields descriptions from the model
        var field_descr_def = model.call('fields_get', [])
            .then(function (fs) { fields = fs; });

        return $.when(important_fields_def, field_descr_def)
            .then(function () {
                self.data = {
                    model: model,
                    domain: domain,
                    fields: fields,
                    important_fields: important_fields,
                    measure: measure,
                    measure_label: fields[measure].string,
                    col_groupby: [],
                    row_groupby: row_groupby,
                    groups: [],
                    total: null,
                };
            });
    },

    display_data : function () {
        var content = this.$el.filter('.graph_main_content');
        content.find('svg').remove();
        var self = this;
        if (this.mode === 'pivot') {
            this.pivot_table.show();
        } else {
            this.pivot_table.hide();
            content.append('<svg></svg>');
            var view_fields = this.data.row_groupby.concat(this.data.measure, this.data.col_groupby);
            query_groups(this.data.model, view_fields, this.data.domain, this.data.row_groupby).then(function (groups) {
                Charts[self.mode](groups, self.data.measure, self.data.measure_label);
            });

        }
    },

    do_search: function (domain, context, group_by) {
        this.data.domain = new instance.web.CompoundDomain(domain);

        if (this.pivot_table) {
            this.pivot_table.draw();
        } else {
            this.pivot_table = new PivotTable(this.data);
            this.pivot_table.appendTo('.graph_main_content');
        }
        this.display_data();
    },

    do_show: function () {
        this.do_push_state({});
        return this._super();
    },

});



 /**
  * PivotTable widget.  It displays the data in tabular data and allows the
  * user to drill down and up in the table
  */
var PivotTable = instance.web.Widget.extend({
    template: 'pivot_table',
    data: null,
    headers: [],
    rows: [],
    cols: [],
    current_row_id : 0,

    events: {
        'click .web_graph_click' : function (event) {
            var self = this;
            event.preventDefault();
            var row_id = event.target.attributes['data-row-id'].nodeValue;

            var row = this.get_row(row_id);
            if (row.expanded) {
                this.fold_row(row_id);
            } else {
                if (row.path.length < this.data.row_groupby.length) {
                    var field_to_expand = this.data.row_groupby[row.path.length];
                    this.expand_row(row_id, field_to_expand);
                } else {
                    var already_grouped = self.data.row_groupby.concat(self.data.col_groupby);
                    var possible_groups = _.difference(self.data.important_fields, already_grouped);
                    var dropdown_options = {
                        fields: _.map(possible_groups, function (field) {
                            return {id: field, value: self.get_descr(field)};
                        }),
                        row_id: row_id,
                    };
                    this.dropdown = $(QWeb.render('field_selection', dropdown_options));
                    $(event.target).after(this.dropdown);
                    this.dropdown.css({position:'absolute',
                                       left:event.pageX,
                                       top:event.pageY});
                    $('.field-selection').next('.dropdown-menu').toggle();
                }
            }

        },
        'click a.field-selection' : function (event) {
            event.preventDefault();
            this.dropdown.remove();
            var row_id = event.target.attributes['data-row-id'].nodeValue;
            var field_id = event.target.attributes['data-field-id'].nodeValue;
            this.expand_row(row_id, field_id);
        },
    },
    
    init: function (data) {
        this.data = data;
    },

    start: function () {
        var self = this;
        this.get_groups(this.data.row_groupby)
            .then(function (groups) {
                self.data.groups = groups;
                return self.get_groups([]);
            }).then(function (total) {
                self.data.total = total;
                self.build_table();
                self.draw();
            });
    },

    draw: function () {
        var self = this;
        this.$el.empty();

        _.each(this.headers, function (header) {
            self.$el.append(header);
        });

        _.each(this.rows, function (row) {
            self.$el.append(row.html);
        });
    },

    show: function () {
        this.$el.css('display', 'block');
    },

    hide: function () {
        this.$el.css('display', 'none');
    },

    build_table: function () {
        var self = this;

        this.headers.push('<tr class="graph_table_header"><td class="graph_border">' +
                    '</td><td class="graph_border">' +
                    this.data.measure_label +
                    '</td></tr>');

        var main_row = this.make_row(this.data.total[0]);

        _.each(this.data.groups, function (group) {
            self.make_row(group, main_row.id);
        });
    },

    get_descr: function (field_id) {
        return this.data.fields[field_id].string;
    },

    get_groups: function (groupby) {
        var view_fields = this.data.row_groupby.concat(this.data.measure, this.data.col_groupby);
        return query_groups(this.data.model, view_fields, this.data.domain, groupby);
    },

    make_row: function (group, parent_id) {
        var path,
            value,
            expanded,
            domain,
            parent,
            has_parent = (parent_id !== undefined),
            row_id = this.generate_id();

        if (has_parent) {
            parent = this.get_row(parent_id);
            path = parent.path.concat(group.attributes.grouped_on);
            value = group.attributes.value[1];
            expanded = false;
            parent.children.push(row_id);
            domain = group.model._domain;
        } else {
            parent = null;
            path = [];
            value = 'Total';
            expanded = true;
            domain = this.data.domain;
        }

        var jquery_row = $('<tr></tr>');

        var header = this.make_cell(value, {is_border:true, indent: path.length, foldable:true, row_id: row_id});
        jquery_row.html(header);
        jquery_row.append(this.make_cell(group.attributes.aggregates[this.data.measure]));

        var row = {
            id: row_id,
            path: path,
            value: value,
            expanded: expanded,
            parent: parent_id,
            children: [],
            html: jquery_row,
            domain: domain,
        };
        this.rows.push(row);  // to do, insert it properly, after all childs of parent
        return row;
    },

    generate_id: function () {
        this.current_row_id += 1;
        return this.current_row_id - 1;
    },

    get_row: function (id) {
        return _.find(this.rows, function(row) {
            return (row.id == id);
        });
    },

    make_cell: function (content, options) {
        options = _.extend({is_border: false, indent:0, foldable:false}, options);
        content = (content) ? content : 'Undefined';

        var cell = $('<td></td>');
        if (options.is_border) cell.addClass('graph_border');
        _.each(_.range(options.indent), function () {
            cell.prepend($('<span/>', {class:'web_graph_indent'}));
        });

        if (options.foldable) {
            var plus = $('<span/>', {'data-row-id':options.row_id,
                                     class:'icon-plus-sign web_graph_click',
                                     href:'#'});
            plus.append(' ');
            plus.append(content);
            cell.append(plus);
        } else {
            cell.append(content);
        }
        return cell;
    },

    expand_row: function (row_id, field_id) {
        var self = this;
        var row = this.get_row(row_id);

        if (row.path.length == this.data.row_groupby.length) {
            this.data.row_groupby.push(field_id);
        }
        row.expanded = true;
        row.html.find('.icon-plus-sign')
            .removeClass('icon-plus-sign')
            .addClass('icon-minus-sign');

        var visible_fields = this.data.row_groupby.concat(this.data.col_groupby, this.data.measure);
        query_groups(this.data.model, visible_fields, row.domain, [field_id])
            .then(function (data) {
                _.each(data.reverse(), function (datapt) {
                    var new_row = self.make_row(datapt, row_id);
                    row.html.after(new_row.html);
                    
                });
        });

    },

    fold_row: function (row_id) {
        var self = this;
        var row = this.get_row(row_id);

        _.each(row.children, function (child_row) {
            self.remove_row(child_row);
        });
        row.children = [];

        row.expanded = false;
        row.html.find('.icon-minus-sign')
            .removeClass('icon-minus-sign')
            .addClass('icon-plus-sign');

        var fold_levels = _.map(self.rows, function(g) {return g.path.length;});
        var new_groupby_length = _.reduce(fold_levels, function (x, y) {
            return Math.max(x,y);
        }, 0);

        this.data.row_groupby.splice(new_groupby_length);
    },

    remove_row: function (row_id) {
        var self = this;
        var row = this.get_row(row_id);

        _.each(row.children, function (child_row) {
            self.remove_row(child_row);
        });

        row.html.remove();
        removeFromArray(this.rows, row);
    },

});

};
