"use strict";
const XU = require("@sembiance/xu"),
	fileUtil = require("@sembiance/xutil").file,
	runUtil = require("@sembiance/xutil").run,
	fs = require("fs"),
	path = require("path"),
	tiptoe = require("tiptoe");

// Will read length bytes from filePath at offset and compare to compareTo
exports.compareFileBytes = function compareFileBytes(filePath, offset, compareTo)
{
	const buf = Buffer.alloc(compareTo.length);
	const fd = fs.openSync(filePath, "r");
	const bytesRead = fs.readSync(fd, buf, 0, compareTo.length, offset);
	fs.closeSync(fd);

	if(bytesRead!==compareTo.length || !buf.equals(compareTo))
		return false;

	return true;
};

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

// Will delete the given filePath, if it exists
exports.unlink = function unlink(filePath)
{
	return (state, p, cb) =>
	{
		tiptoe(
			function getExistance()
			{
				fileUtil.exists(filePath, this);
			},
			function performCheck(fileExists)
			{
				if(!fileExists)
					return this();

				fileUtil.unlink(filePath, this);
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
	state.cwd = state.tmpCWD = fileUtil.generateTempFilePath(undefined, "");

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

	if(state.output?.original)
	{
		state.output.dirPath = state.output.original;
		delete state.output.original;
	}

	tiptoe(
		function removeTmpCWD()
		{
			// Keep the tmp dir around if we are verbose level 4+
			if(state.verbose>=5)
				return this();

			fileUtil.unlink(state.tmpCWD, this);
		},
		function removeOriginalCWDKey()
		{
			state.cwd = state.originalCWD;
			delete state.originalCWD;
			if(state.verbose<5)
				delete state.tmpCWD;

			this();
		},
		cb
	);
};

// Returns a step function that will create a 'safe' filename (no unicode chars, short, etc) for programs to use by symlinking to the original
exports.safeInput = function safeInput(filename, ext, noSymlink)
{
	return (state, p, cb) =>
	{
		const safeRelativeFilePath = filename + ext;

		state.input.original = state.input.filePath;
		state.input.filePath = safeRelativeFilePath;
		state.input.dirPath = path.dirname(state.input.absolute);

		const outputFilePath = path.join(state.cwd, safeRelativeFilePath);

		if(noSymlink)
			fs.copyFile(state.input.absolute, outputFilePath, cb);
		else
			fs.symlink(state.input.absolute, outputFilePath, cb);
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

// Will find any output files that have been created, are not empty, are not identical to input and store it into state.meta.output
exports.findValidOutputFiles = function findValidOutputFiles(force)
{
	return (state, p, cb) =>
	{
		if(!force && state.output.files)
			return setImmediate(cb);
		
		tiptoe(
			function findFiles()
			{
				if(state.verbose>=4)
					XU.log`file.findValidOutputFiles starting glob to find output files...`;

				fileUtil.glob(state.output.absolute, "**", {nodir : true}, this);
			},
			function gatherOutputFileInfo(outputFilePaths)
			{
				if(state.verbose>=4)
					XU.log`file.findValidOutputFiles found ${outputFilePaths.length} output files. Checking for zero length files and src duplicates...`;

				delete state.output.files;

				if(outputFilePaths.length===0)
					return this.finish();
				
				this.data.outputFilePaths = outputFilePaths;

				// Find is very fast at finding and eleting empty files, so let's use that instead of running stat on every output file and checking then deleting myself
				runUtil.run("find", [state.output.absolute, "-type", "f", "-empty", "-delete", "-print"], runUtil.SILENT, this.parallel());

				// If we have only 1 output file, make sure it's not identical to our src file, if it is we will delete it to prevent infinite recursion
				// We assume that if we can produce more than 1 output file that it's unlikely we can have a sub file identical to our parent
				if(outputFilePaths.length===1)
					fileUtil.areEqual(state.input.absolute, outputFilePaths[0], this.parallel());
			},
			function removeEmptyOutputFiles(deletedFilePathsRaw, outputFileEqual)
			{
				const badOutputFiles = deletedFilePathsRaw.trim().split("\n").filterEmpty();
				if(state.verbose>=4 && badOutputFiles.length>0)
					XU.log`file.findValidOutputFiles deleted ${badOutputFiles} empty output files.`;

				if(this.data.outputFilePaths.length===1 && outputFileEqual)
				{
					XU.log`file.findValidOutputFiles is deleting the single output file ${this.data.outputFilePaths[0]} due to it being identical to the src file`;
					fileUtil.unlink(this.data.outputFilePaths[0], this.parallel());
					badOutputFiles.push(this.data.outputFilePaths[0]);
				}

				state.output.files = this.data.outputFilePaths.subtractAll(badOutputFiles).map(outputFilePath => path.relative(state.output.absolute, outputFilePath));
				if(state.output.files.length===0)
					delete state.output.files;

				this.parallel()();
			},
			cb
		);
	};
};

// Will move the file from fromPath to toPath, if it exists that is
exports.copy = function move(fromPath, toPath)
{
	return (state, p, cb) =>
	{
		if(state.verbose>=5)
			XU.log`Attempting to copy file ${fromPath} to ${toPath}`;

		tiptoe(
			function checkForOutputFile()
			{
				fileUtil.exists(fromPath, this);
			},
			function performMove(exists)
			{
				if(!exists)
				{
					if(state.verbose>=5)
						XU.log`Unable to copy file ${fromPath} to ${toPath} as it does not exist!`;
					return this();
				}
				
				fs.copyFile(fromPath, toPath, this);
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
		if(state.verbose>=5)
			XU.log`Attempting to move file ${fromPath} to ${toPath}`;

		tiptoe(
			function checkForOutputFile()
			{
				fileUtil.exists(fromPath, this);
			},
			function performMove(exists)
			{
				if(!exists)
				{
					if(state.verbose>=5)
						XU.log`Unable to move file ${fromPath} to ${toPath} as it does not exist!`;
					return this();
				}
				
				fileUtil.move(fromPath, toPath, this);
			},
			cb
		);
	};
};

// Will move all files in fromDirPath/* to toDirPath/*
exports.moveAllFiles = function moveAllFiles(fromDirPath, toDirPath)
{
	return (state, p, cb) =>
	{
		tiptoe(
			function findFiles()
			{
				fileUtil.glob(fromDirPath, "*", {nodir : true}, this);
			},
			function moveFiles(filePaths)
			{
				if(!filePaths || filePaths.length===0)
					return this.finish();
				
				filePaths.parallelForEach((filePath, subcb) => fileUtil.move(filePath, path.join(toDirPath, path.basename(filePath)), subcb), this);
			},
			cb
		);
	};
};
