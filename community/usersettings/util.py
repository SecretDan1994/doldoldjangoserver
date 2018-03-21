# wip - ensure user setting and its validator - with statement?

class _user_settings_ensure(object):
	def __init__(self):
		self.delayed_execute = []

	def __call__(self, *args, **kwargs):
		self.model = apps.get_model("usersettings", "UserSetting")

		self.__call__ = self.__call__loaded
		for args, kwargs in self.delayed_execute:
			self.__call__(*args, **kwargs)
		self.__call__(*args, **kwargs)

	def __call__loaded(self, *args, **kwargs):
		self.model.ensure(*args, **kwargs)

	def on_ready(self):
		self.model = apps.get_model("usersettings", "UserSetting")
		self.__call__ = self.__call__loaded
		for args, kwargs in self.delayed_execute:
			self.__call__(*args, **kwargs)


user_setting_ensure = _user_settings_ensure()