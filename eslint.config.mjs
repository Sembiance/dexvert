import {default as denoConfig} from "/mnt/compendium/DevLab/common/eslint/deno.eslint.config.js";

denoConfig.push({
	ignores :
	[
		"aux/",
		"bin/amiga-bitmap-font-tools/",
		"blender/",
		"classify/",
		"dos/",
		"music/",
		"os/",
		"sandbox/",
		"scribus/",
		"test/model-viewer.min.js",
		"test/recurse/",
		"test/sample/",
		"texmf/",
		"wine/"
	]
});

export default denoConfig;	// eslint-disable-line unicorn/prefer-export-from
