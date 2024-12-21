import {default as denoConfig} from "/mnt/compendium/DevLab/common/eslint/deno.eslint.config.js";

denoConfig.push({
	rules :
	{
		"@stylistic/no-multi-spaces"             : 0,
		"new-cap"                                : 0,
		"@stylistic/lines-between-class-members" : 0,
		"prefer-named-capture-group"             : 0
	}
});

export default denoConfig;	// eslint-disable-line unicorn/prefer-export-from
