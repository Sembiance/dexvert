import {default as denoConfig} from "/mnt/compendium/DevLab/common/eslint/deno.eslint.config.js";

denoConfig.push({
	rules :
	{
		"unicorn/empty-brace-spaces" : 0
	}
});

export default denoConfig;	// eslint-disable-line unicorn/prefer-export-from
