import {default as denoConfig} from "/mnt/compendium/DevLab/common/eslint/deno.eslint.config.js";

denoConfig.push({
	rules :
	{
		// Program classes have public properties that use spaces for better formatting
		"@stylistic/no-multi-spaces"             : 0,
		"@stylistic/lines-between-class-members" : 0,

		// Program class names replace dashes with underscores
		"camelcase" : 0
	}
});

export default denoConfig;	// eslint-disable-line unicorn/prefer-export-from
