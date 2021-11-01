"use strict";
const XU = require("@sembiance/xu"),
	fs = require("fs"),
	fileUtil = require("@sembiance/xutil").file,
	path = require("path");

exports.meta =
{
	website       : "https://github.com/Samsung/rlottie",
	gentooPackage : "media-libs/rlottie"
};

exports.bin = () => "lottie2gif";
exports.args = (state, p, r, inPath=state.input.filePath) =>
{
	const parsed = XU.parseJSON(fs.readFileSync(state.input.absolute, XU.UTF8), {});
	const args = [inPath];
	if(parsed.w && parsed.h)
		args.push(`${parsed.w}x${parsed.h}`);

	return args;
};
exports.cwd = state => state.output.absolute;

exports.pre = (state, p, r, cb) =>
{
	// Some lottie files include image assets. Let's copy them over into the output dir (which is our CWD). We'll delete them after we are done
	const parsed = XU.parseJSON(fs.readFileSync(state.input.absolute, XU.UTF8), null);
	if(!parsed || !parsed.assets)
		return setImmediate(cb);

	parsed.assets.parallelForEach((asset, subcb) =>
	{
		if(!asset.u || !asset.p)
			return setImmediate(subcb);

		const subPath = path.join(asset.u, asset.p);
		const srcInPath = path.join(state.input.dirPath, subPath);
		if(!fileUtil.existsSync(srcInPath))
			return setImmediate(subcb);

		if(!r.lottieCreatedDirs)
			r.lottieCreatedDirs = [];
		const assetDirPath = path.join(state.cwd, asset.u);
		r.lottieCreatedDirs.push(assetDirPath);
		fs.mkdirSync(assetDirPath, {recursive : true});
		fs.copyFile(srcInPath, path.join(state.cwd, subPath), subcb);
	}, cb);
};

exports.post = (state, p, r, cb) => (r.lottieCreatedDirs || []).serialForEach((lottieCreatedDir, subcb) => fileUtil.unlink(lottieCreatedDir, subcb), cb);
