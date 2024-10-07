# toggle_manager.py


class ToggleMethod:
    def __init__(self, instance, method_name, configs):
        """Initialize with the instance, method name, and configurations."""
        self.instance = instance
        self.method_name = method_name
        self.method = getattr(self.instance, self.method_name, None)

        # Check if method exists at initialization
        if not callable(self.method):
            raise ValueError(f"Method '{self.method_name}' not found on instance.")

        self.configs = configs  # Dictionary of toggle configurations
        self.toggle_state = {config_name: {key: 0 for key in config} for config_name, config in configs.items()}
        self.conditions = {}

    def add_condition(self, config_name, param, condition_func):
        """Add a custom condition for toggling behavior."""
        if config_name not in self.conditions:
            self.conditions[config_name] = {}
        self.conditions[config_name][param] = condition_func

    def add_conditions(self, config_name, conditions_dict):
        """Add multiple conditions to a specific configuration for a method."""
        if config_name not in self.conditions:
            self.conditions[config_name] = {}
        self.conditions[config_name].update(conditions_dict)

    def apply_toggles(self, config_name, *args, **kwargs):
        """Apply the toggles and call the pre-resolved method dynamically for a specific configuration."""
        if config_name not in self.configs:
            raise ValueError(f"Configuration '{config_name}' not found for method '{self.method_name}'.")

        config_toggles = self.configs[config_name]
        config_state = self.toggle_state[config_name]

        for param, param_info in config_toggles.items():
            values = param_info.get('values', [])
            default_value = param_info.get('default', None)

            if config_name in self.conditions and param in self.conditions[config_name]:
                condition = self.conditions[config_name][param]
                condition_value = condition(args, values)

                if condition_value is not None:
                    kwargs[param] = condition_value
                elif default_value is not None:
                    kwargs[param] = default_value
            elif default_value is not None or len(values) > 0:
                current_value = values[config_state[param]]
                kwargs[param] = current_value

                # Increment the index for the current parameter
                config_state[param] = (config_state[param] + 1) % len(values)

        # Call the pre-resolved method with toggled parameters
        self.method(*args, **kwargs)


class ToggleManager:
    def __init__(self, instance):
        """Initialize the ToggleManager with the instance."""
        self.instance = instance
        self.methods = {}

    def add_method(self, method_name, configs):
        """Register a new method with multiple toggle configurations."""
        self.methods[method_name] = ToggleMethod(self.instance, method_name, configs)

    def add_condition(self, method_name, config_name, param, condition_func):
        """Add a condition to a specific configuration for a method."""
        if method_name not in self.methods:
            raise ValueError(f"Method '{method_name}' is not registered.")
        self.methods[method_name].add_condition(config_name, param, condition_func)

    def add_conditions(self, method_name, config_name, conditions_dict):
        """Add multiple conditions to a specific configuration for a method."""
        if method_name not in self.methods:
            raise ValueError(f"Method '{method_name}' is not registered.")
        self.methods[method_name].add_conditions(config_name, conditions_dict)


    def toggle_method(self, method_name, config_name='default', *args, **kwargs):
        """Apply the toggles and call the registered method using the pre-resolved reference."""
        if method_name not in self.methods:
            raise ValueError(f"Method '{method_name}' is not registered.")
        self.methods[method_name].apply_toggles(config_name, *args, **kwargs)

    def get_toggled_method(self, method_name):
        if method_name not in self.methods:
            raise ValueError(f"Method '{method_name}' is not registered.")
        return lambda *args, config_name='default', **kwargs: \
            self.methods[method_name].apply_toggles(config_name, *args, **kwargs)

    def __getattr__(self, name):
        if name in self.methods:
            def method(*args, config_name='default', **kwargs):
                self.methods[name].apply_toggles(config_name, *args, **kwargs)

            return method
        raise AttributeError(f"'ToggleManager' object has no attribute '{name}'")

