"use strict";
const XU = require("@sembiance/xu"),
	fileUtil = require("@sembiance/xutil").file,
	fs = require("fs"),
	path = require("path"),
	tiptoe = require("tiptoe");

// Checks whether or not filePath exists
exports.exists = function exists(filePath, checkFun, errorMsg="util.file.exists failed")
{
	return (state, {DexvertError}, cb) =>
	{
		tiptoe(
			function getExistance()
			{
				fileUtil.exists(filePath, this);
			},
			function performCheck(fileExists)
			{
				if(!checkFun(fileExists))
					throw new DexvertError(state, errorMsg);

				this();
			},
			cb
		);
	};
};

// Performs a fs.stat on filePath and then you can check for things like size or isDirectory, etc
exports.stat = function stat(filePath, checkFun, errorMsg="util.file.size failed")
{
	return (state, {DexvertError}, cb) =>
	{
		tiptoe(
			function getStat()
			{
				fs.stat(filePath, this);
			},
			function performCheck(fileStat)
			{
				if(!checkFun(fileStat))
					throw new DexvertError(state, errorMsg);

				this();
			},
			cb
		);
	};
};

// Performs a glob() and then runs the checkFun
exports.glob = function glob(dirPath, matchPattern, globOptions, checkFun, errorMsg="util.file.find failed")
{
	return (state, {DexvertError}, cb) =>
	{
		tiptoe(
			function getStat()
			{
				fileUtil.glob(dirPath, matchPattern, globOptions, this);
			},
			function performCheck(globResults)
			{
				if(!checkFun(globResults))
					throw new DexvertError(state, errorMsg);

				this();
			},
			cb
		);
	};
};

// Creates a temporary working directory for future actions. input/output are a already absolute paths, so don't need to modify those
exports.tmpCWDCreate = function tmpCWDCreate(state, p, cb)
{
	state.originalCWD = state.cwd;
	state.cwd = state.tmpCWD = fileUtil.generateTempFilePath(state.tmpDirPath, "");

	fs.mkdir(state.cwd, {recursive : true}, cb);
};

// Removes the temporary working directory and all files under it
exports.tmpCWDCleanup = function tmpCWDCleanup(state, p, cb)
{
	// Only do this if we've changed the CWD
	if(!state.originalCWD || !state.tmpCWD)
		return setImmediate(cb);

	if(state.input.original)
	{
		state.input.filePath = state.input.original;
		delete state.input.original;
	}

	if(state.output.original)
	{
		state.output.dirPath = state.output.original;
		delete state.output.original;
	}

	tiptoe(
		function removeTmpCWD()
		{
			fileUtil.unlink(state.tmpCWD, this);
		},
		function removeOriginalCWDKey()
		{
			state.cwd = state.originalCWD;
			delete state.originalCWD;
			delete state.tmpCWD;

			this();
		},
		cb
	);
};

// Returns a step function that will create a 'safe' filename (no unicode chars, short, etc) for programs to use by symlinking to the original
exports.safeInput = function safeInput(ext)
{
	return (state, p, cb) =>
	{
		const safeRelativeFilePath = "in" + ext;

		state.input.original = state.input.filePath;
		state.input.filePath = safeRelativeFilePath;

		fs.symlink(state.input.absolute, path.join(state.cwd, safeRelativeFilePath), cb);
	};
};

// Creates a 'safe' output directory name (no unicode chars, short, etc) for programs to use by symlinking to the original output dirPath
exports.safeOutput = function safeOutput(state, p, cb)
{
	const safeRelativeDirPath = "out";

	state.output.original = state.output.dirPath;
	state.output.dirPath = safeRelativeDirPath;

	fs.symlink(state.output.absolute, path.join(state.cwd, safeRelativeDirPath), cb);
};

// Will find any output files that have been created and store it into state.meta.output
exports.findOutputFiles = function findOutputFiles(force)
{
	return (state, p, cb) =>
	{
		if(!force && state.output.files)
			return setImmediate(cb);
		
		tiptoe(
			function findFiles()
			{
				fileUtil.glob(state.output.absolute, "**", {nodir : true}, this);
			},
			function recordFilesToState(outputFilePaths)
			{
				delete state.output.files;

				if(outputFilePaths.length===0)
					return this();
				
				state.output.files = outputFilePaths.map(outputFilePath => path.relative(state.output.absolute, outputFilePath));
			
				this();
			},
			cb
		);
	};
};

// Will move the file from fromPath to toPath, if it exists that is
exports.move = function move(fromPath, toPath)
{
	return (state, p, cb) =>
	{
		tiptoe(
			function checkForOutputFile()
			{
				fileUtil.exists(fromPath, this);
			},
			function performMove(exists)
			{
				if(!exists)
					return this();
				
				fileUtil.move(fromPath, toPath, this);
			},
			cb
		);
	};
};
