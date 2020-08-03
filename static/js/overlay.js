function Overlay() {
	var self = this;
	
	self.isVisible = ko.observable(false);
	self.title = ko.observable();
	self.pageYOffset = ko.pureComputed(function () {
        return self.isVisible() ? window.pageYOffset + 'px': '0px';
    });
	self.template = ko.observable('defaultTmpl');
	self.afterRender = ko.observable(function (elements) {
		return elements;
	});
	
	self.show = function () {
		self.isVisible(true);
	};
	
	self.hide = function () {
		self.isVisible(false);
	};
}
