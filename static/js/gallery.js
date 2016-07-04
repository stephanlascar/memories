$(function () {

    var Picture = Backbone.Model.extend({
        idAttribute: '_id',

        initialize: function () {
            this.computedFields = new Backbone.ComputedFields(this);
        },

        computed: {
            aspect_ratio: {
                depends: ['resolution'],
                get: function (field) {
                    return field.resolution.width / field.resolution.height;
                }
            }
        }

    });

    var Pictures = Backbone.Collection.extend({
        model: Picture,

        url: '/api/v1/images',

        comparator: function(obj) {
            return new Date(obj.get("shot") || obj.get("inserted")) * -1;
        }
    });

    var GalleryPicture = Backbone.View.extend({
        className: 'photo',

        events: {
            'click': 'onClick'
        },

        onClick: function (event) {
            Backbone.Mediator.publish('photo:selected', this.model);
        },

        render: function (width, height) {
            this.$el.css({
                width: width - 4,
                height: height - 4,
                'background-image': "url('/thumbnail/" + this.model.get('thumbnail') + "')"
            });

            return this;
        }

    });

    var Gallery = Backbone.View.extend({
        id:'images',

        initialize: function() {
            this.ideal_height = parseInt($(window).height() / 2.5);
            $(window).bind('resize', _.bind(_.debounce(this.resize, 100), this));
            this.listenTo(this.collection, 'destroy', this.onDelete);
        },

        onDelete: function () {
            refresh();
        },

        resize: function () {
            this.$el.html('');
            this.render.call(this);
        },

        remove: function() {
            $(window).unbind('resize');
            Backbone.View.prototype.remove.call(this);
        },

        render: function () {
            var that = this;

            this.viewport_width = this.$el.width() - 15;
            var summed_width = _.reduce(this.collection.models, function(sum, photo) {
                return sum + photo.get('aspect_ratio') * that.ideal_height;
            }, 0);

            var number_of_rows = Math.round(summed_width / that.viewport_width);
            var weights = _.map(this.collection.models, function(picture) {
                return parseInt(picture.get('aspect_ratio') * 100);
            });
            var partition = linear_partition(weights, number_of_rows);

            var index = 0;
            var row_buffer = new Backbone.Collection();

            _.each(partition, function(row) {
                row_buffer.reset();
                _.each(row, function() {
                    row_buffer.add(that.collection.at(index++));
                });

                var summed_ratios = _.reduce(row_buffer.models, function(sum, photo) {
                    return sum + photo.get('aspect_ratio');
                }, 0);

                _.each(row_buffer.models, function (picture) {
                    var height = parseInt(that.viewport_width / summed_ratios);
                    var width = parseInt(that.viewport_width / summed_ratios * picture.get('aspect_ratio'));
                    that.$el.append(new GalleryPicture({model: picture}).render(width, height).$el);
                });
            });

            return this;
        }
    });

    var Modal = Backbone.View.extend({
        className: 'modal',
        template: _.template(modal_template),
        events: {
            'click button.btn-default': 'close',
            'click button.btn-danger': 'delete'
        },

        render: function () {
            this.$el.html(this.template());
            return this;
        },

        close: function () {
            this.$el.remove();
            this.remove();
        },

        delete: function () {
            var that = this;
            this.model.destroy({
                success: function () {
                    that.close();
                }
            });
        },

        show: function () {
            $('body').append(this.$el);
        }

    });

    var ToolBar = Backbone.View.extend({
        template: _.template(tool_bar_template),

        events: {
            'click div.toggle': 'toggle',
            'click li.delete': 'delete',
            'click li.exif': 'onClickExif'
        },

        initialize: function () {
            Backbone.Mediator.subscribe('photo:selected', this.on_photo_selected, this);
        },

        onClickExif: function() {
          alert("coucou");
        },

        delete: function () {
            new Modal({model: this.model}).render().show();
        },

        on_photo_selected: function (photo) {
            this.model = photo;
            this.$el.find('.shot').html(moment(this.model.get('shot')).format('dddd Do MMMM YYYY à HH:mm:ss'));
            this.$el.removeClass('disabled');
        },

        toggle: function(event) {
            this.$el.toggleClass('open');
            $(window).trigger('resize');
        },

        render: function() {
            this.$el.html(this.template());
            return this;
        }

    });

    var page = 0;
    var next_page = _.debounce(function() {
        new Pictures().fetch({
            data: {page: ++page},
            success: function (pictures) {
                new Gallery({el: $('#content'), collection: pictures}).render();
            }
        });
    }, 1000);

    var refresh = function() {
        for(var i = 1 ; i < page ; i++) {
          new Pictures().fetch({
              data: {page: i},
              success: function (pictures) {
                  new Gallery({el: $('#content'), collection: pictures}).render();
              }
          });
        }
    };

    next_page();

    $('#content').bind('scroll', function() {
        if($('#content').scrollTop() + $('#content').height() + 100 >= $('#content').prop('scrollHeight')) {
            next_page();
        }
    });

    new ToolBar({el: $('#tool-bar')}).render();

});