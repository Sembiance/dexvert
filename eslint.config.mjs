import {default as denoConfig} from "/mnt/compendium/DevLab/common/eslint/deno.eslint.config.js";

denoConfig.push({
	ignores :
	[
		"aux/",
		"bin/amiga-bitmap-font-tools/",
		"bin/mmf2vgm.js",
		"blender/",
		"classify/",
		"dos/",
		"music/",
		"os/",
		"sandbox/",
		"scribus/",
		"test/model-viewer.min.js",
		"test/recurse/expected/",
		"test/recurse/sample/",
		"test/sample/",
		"texmf/",
		"wine/"
	]
});

export default denoConfig;	// eslint-disable-line unicorn/prefer-export-from
