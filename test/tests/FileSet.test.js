import {FileSet} from "../../src/FileSet.js";
import {DexFile} from "../../src/DexFile.js";
import {fileUtil} from "xutil";
import {path, base64Encode, assertStrictEquals, assertRejects, assertEquals, assert} from "std";

const fileSetJSON = `{"root":"/mnt/compendium/DevLab/dexvert/test/files","files":{"input":[{"root":"/mnt/compendium/DevLab/dexvert/test/files","rel":"some.big.txt.file.txt","absolute":"/mnt/compendium/DevLab/dexvert/test/files/some.big.txt.file.txt","base":"some.big.txt.file.txt","dir":"/mnt/compendium/DevLab/dexvert/test/files","name":"some.big.txt.file","ext":".txt","preExt":".some","preName":"big.txt.file.txt","isFile":true,"isDirectory":false,"isSymlink":false,"size":6,"ts":1635688339000},{"root":"/mnt/compendium/DevLab/dexvert/test/files","rel":"subDir/txt.b","absolute":"/mnt/compendium/DevLab/dexvert/test/files/subDir/txt.b","base":"txt.b","dir":"/mnt/compendium/DevLab/dexvert/test/files/subDir","name":"txt","ext":".b","preExt":".txt","preName":"b","isFile":true,"isDirectory":false,"isSymlink":false,"size":8,"ts":1635685484995},{"root":"/mnt/compendium/DevLab/dexvert/test/files","rel":"subDir/more_sub/third","absolute":"/mnt/compendium/DevLab/dexvert/test/files/subDir/more_sub/third","base":"third","dir":"/mnt/compendium/DevLab/dexvert/test/files/subDir/more_sub","name":"third","ext":"","preExt":"","preName":"third","isFile":false,"isDirectory":true,"isSymlink":false,"size":4096,"ts":1635685489475}],"other":[{"root":"/mnt/compendium/DevLab/dexvert/test/files","rel":"subDir/symlinkFile","absolute":"/mnt/compendium/DevLab/dexvert/test/files/subDir/symlinkFile","base":"symlinkFile","dir":"/mnt/compendium/DevLab/dexvert/test/files/subDir","name":"symlinkFile","ext":"","preExt":"","preName":"symlinkFile","isFile":false,"isDirectory":false,"isSymlink":true,"size":14,"ts":1635685795866},{"root":"/mnt/compendium/DevLab/dexvert/test/files","rel":"subDir/more_sub/c.txt","absolute":"/mnt/compendium/DevLab/dexvert/test/files/subDir/more_sub/c.txt","base":"c.txt","dir":"/mnt/compendium/DevLab/dexvert/test/files/subDir/more_sub","name":"c","ext":".txt","preExt":".c","preName":"txt","isFile":true,"isDirectory":false,"isSymlink":false,"size":10,"ts":1635685592959}]}}`; // eslint-disable-line max-len

Deno.test("addFile", async () =>
{
	let a = await FileSet.create("/mnt/compendium/DevLab/dexvert/test/files", "input", [
		"/mnt/compendium/DevLab/dexvert/test/files/some.big.txt.file.txt",
		"/mnt/compendium/DevLab/dexvert/test/files/subDir/txt.b"]);
	await a.add("input", "/mnt/compendium/DevLab/dexvert/test/files/subDir/symlinkFile");
	await a.add("input", "/mnt/compendium/DevLab/dexvert/test/files/subDir/more_sub/c.txt");
	await a.add("input", "/mnt/compendium/DevLab/dexvert/test/files/subDir/more_sub/third");
	const b = await FileSet.create("/mnt/compendium/DevLab/dexvert/test/files", "input", [
		"/mnt/compendium/DevLab/dexvert/test/files/some.big.txt.file.txt",
		"/mnt/compendium/DevLab/dexvert/test/files/subDir/txt.b"]);
	await b.addAll("input", ["/mnt/compendium/DevLab/dexvert/test/files/subDir/symlinkFile", "/mnt/compendium/DevLab/dexvert/test/files/subDir/more_sub/c.txt", "/mnt/compendium/DevLab/dexvert/test/files/subDir/more_sub/third"]);

	[a, b].forEach(o =>
	{
		assertStrictEquals(o.root, "/mnt/compendium/DevLab/dexvert/test/files");
		assertStrictEquals(o.files.input.length, 5);
		assertStrictEquals(o.all.length, 5);
		assertStrictEquals(o.input.name, "some.big.txt.file");
		assertStrictEquals(o.input.size, 6);
		assertStrictEquals(o.files.input[2].isSymlink, true);
		assertStrictEquals(o.all[2].isSymlink, true);
		assertStrictEquals(o.files.input[2].isSymlink, true);
	});

	assertRejects(async () => await a.add(await DexFile.create("/mnt/compendium/DevLab/dexvert/.gitignore")));
	assertRejects(async () => await a.add(await DexFile.create("whatever", "/mnt/compendium/DevLab/dexvert/.gitignore")));

	await a.add("input", "/mnt/compendium/DevLab/dexvert/test/files/subDir/more_sub/c.txt");
	assertStrictEquals(a.files.input.length, 5);

	// test modifying a file and adding it back
	const tmpFilePath = await fileUtil.genTempPath();
	await fileUtil.writeTextFile(tmpFilePath, "abc\n123");
	a = await FileSet.create(path.dirname(tmpFilePath), "test", tmpFilePath);
	assertStrictEquals(a.test.base, path.basename(tmpFilePath));
	assertStrictEquals(a.test.size, 7);
	await fileUtil.writeTextFile(tmpFilePath, "Hello, World!");
	assertStrictEquals(a.test.base, path.basename(tmpFilePath));
	assertStrictEquals(a.test.size, 7);
	await a.add("test", tmpFilePath);
	assertStrictEquals(a.test.base, path.basename(tmpFilePath));
	assertStrictEquals(a.test.size, 13);
	await fileUtil.unlink(tmpFilePath);
});

Deno.test("changeRoot", async () =>
{
	let a = await FileSet.create("/mnt/compendium/DevLab/dexvert/test/files/", "input", ["some.big.txt.file.txt", "subDir/txt.b", "subDir/symlinkFile", "subDir/more_sub/c.txt", "subDir/more_sub/third"]);
	const b = await a.clone();
	b.changeRoot("/some/other/dir/", {keepRel : true});

	// test original
	assertStrictEquals(a.root, "/mnt/compendium/DevLab/dexvert/test/files");
	assertStrictEquals(a.files.input.length, 5);
	assertStrictEquals(a.all.length, 5);
	assertStrictEquals(a.input.name, "some.big.txt.file");
	assertStrictEquals(a.input.size, 6);
	assertStrictEquals(a.all[2].isSymlink, true);
	assertStrictEquals(a.files.input[2].isSymlink, true);
	assertStrictEquals(a.all[2].rel, "subDir/symlinkFile");

	// test clone
	assertStrictEquals(b.root, "/some/other/dir");
	assertStrictEquals(b.files.input.length, 5);
	assertStrictEquals(b.all.length, 5);
	assertStrictEquals(b.input.name, "some.big.txt.file");
	assertStrictEquals(b.input.size, 6);
	assertStrictEquals(b.all[2].isSymlink, true);
	assertStrictEquals(b.files.input[2].isSymlink, true);
	assertStrictEquals(b.all[2].rel, "subDir/symlinkFile");
	assertStrictEquals(b.all[2].root, "/some/other/dir");
	assertStrictEquals(b.all[2].absolute, "/some/other/dir/subDir/symlinkFile");
	assertStrictEquals(b.all[2].dir, "/some/other/dir/subDir");
	assertStrictEquals(b.all[2].name, "symlinkFile");

	a = await FileSet.create("/mnt/compendium/DevLab/dexvert/test/files/", "input", ["some.big.txt.file.txt", "subDir/txt.b", "subDir/symlinkFile", "subDir/more_sub/c.txt", "subDir/more_sub/third"]);
	a.changeRoot("/mnt/compendium/DevLab/dexvert/test/files/subDir/more_sub");
	assertStrictEquals(a.root, "/mnt/compendium/DevLab/dexvert/test/files/subDir/more_sub");
	assertStrictEquals(a.files.input.length, 5);
	assertStrictEquals(a.all.length, 5);
	assertStrictEquals(a.input.name, "some.big.txt.file");
	assertStrictEquals(a.input.size, 6);
	assertStrictEquals(a.all[2].isSymlink, true);
	assertStrictEquals(a.files.input[2].isSymlink, true);
	assertStrictEquals(a.all[2].rel, "../symlinkFile");
	assertStrictEquals(a.all[2].root, "/mnt/compendium/DevLab/dexvert/test/files/subDir/more_sub");
	assertStrictEquals(a.all[2].absolute, "/mnt/compendium/DevLab/dexvert/test/files/subDir/symlinkFile");
	assertStrictEquals(a.all[2].dir, "/mnt/compendium/DevLab/dexvert/test/files/subDir");
	assertStrictEquals(a.all[2].name, "symlinkFile");

	assertStrictEquals(a.all[0].rel, "../../some.big.txt.file.txt");
	assertStrictEquals(a.all[1].rel, "../txt.b");
	assertStrictEquals(a.all[3].rel, "c.txt");
	assertStrictEquals(a.all[4].rel, "third");
});

Deno.test("create", async () =>
{
	const a = await FileSet.create("/mnt/compendium/DevLab/dexvert/test/files", "input", [
		"/mnt/compendium/DevLab/dexvert/test/files/some.big.txt.file.txt",
		"/mnt/compendium/DevLab/dexvert/test/files/subDir/txt.b",
		"/mnt/compendium/DevLab/dexvert/test/files/subDir/symlinkFile",
		"/mnt/compendium/DevLab/dexvert/test/files/subDir/more_sub/c.txt",
		"/mnt/compendium/DevLab/dexvert/test/files/subDir/more_sub/third"]);
	const b = await FileSet.create("/mnt/compendium/DevLab/dexvert/test/files/", "input", ["some.big.txt.file.txt", "subDir/txt.b", "subDir/symlinkFile", "subDir/more_sub/c.txt", "subDir/more_sub/third"]);
	const c = await b.clone();
	const d = await b.clone();
	const e = await FileSet.create("/mnt/compendium/DevLab/dexvert/test/files/", "input", [
		"/mnt/compendium/DevLab/dexvert/test/files/some.big.txt.file.txt",
		"/mnt/compendium/DevLab/dexvert/test/files/subDir/txt.b",
		"/mnt/compendium/DevLab/dexvert/test/files/subDir/symlinkFile",
		"/mnt/compendium/DevLab/dexvert/test/files/subDir/more_sub/c.txt",
		"/mnt/compendium/DevLab/dexvert/test/files/subDir/more_sub/third"]);
	d.changeRoot("/tmp/path/dir", {keepRel : true});

	[a, b, c, e].forEach(o =>
	{
		assertStrictEquals(o.root, "/mnt/compendium/DevLab/dexvert/test/files");
		assertStrictEquals(o.files.input.length, 5);
		assertStrictEquals(o.all.length, 5);
		assertStrictEquals(o.input.name, "some.big.txt.file");
		assertStrictEquals(o.input.size, 6);
		assertStrictEquals(o.all[2].isSymlink, true);
		assertStrictEquals(o.files.input[2].isSymlink, true);
	});
});

Deno.test("clone", async () =>
{
	const a = await FileSet.create("/mnt/compendium/DevLab/dexvert/test/files", "input", [
		"/mnt/compendium/DevLab/dexvert/test/files/some.big.txt.file.txt",
		"/mnt/compendium/DevLab/dexvert/test/files/subDir/txt.b",
		"/mnt/compendium/DevLab/dexvert/test/files/subDir/more_sub/third"]);
	await a.addAll("other", ["/mnt/compendium/DevLab/dexvert/test/files/subDir/symlinkFile", "/mnt/compendium/DevLab/dexvert/test/files/subDir/more_sub/c.txt"]);
	let b = await a.clone();
	assertStrictEquals(b.files.input.length, 3);
	assertStrictEquals(b.files.other.length, 2);
	assertStrictEquals(b.all.length, 5);

	b = await a.clone("other");
	assert(!b.files.input);
	assertStrictEquals(b.files.other.length, 2);
	assertStrictEquals(b.all.length, 2);
});

Deno.test("pretty", async () =>
{
	const a = await FileSet.create("/mnt/compendium/DevLab/dexvert/test/files", "input", [
		"/mnt/compendium/DevLab/dexvert/test/files/some.big.txt.file.txt",
		"/mnt/compendium/DevLab/dexvert/test/files/subDir/txt.b",
		"/mnt/compendium/DevLab/dexvert/test/files/subDir/more_sub/third"]);
	await a.addAll("other", ["/mnt/compendium/DevLab/dexvert/test/files/subDir/symlinkFile", "/mnt/compendium/DevLab/dexvert/test/files/subDir/more_sub/c.txt"]);

	assertStrictEquals(base64Encode(a.pretty()), "RmlsZVNldCAbWzM2bSgbWzBtcm9vdCAbWzM1bS9tbnQvY29tcGVuZGl1bS9EZXZMYWIvZGV4dmVydC90ZXN0L2ZpbGVzG1swbRtbMzZtKRtbMG0gaGFzIBtbMzNtNRtbMG0gZmlsZXM6CgkbWzk3bWlucHV0OiAbWzBtG1szODs1OzI1MG1GG1swbSAbWzk3bSAgICA2YhtbMG0gG1s5NW0vbW50L2NvbXBlbmRpdW0vRGV2TGFiL2RleHZlcnQvdGVzdC9maWxlcxtbMG0bWzk2bS8bWzBtG1s5NW1zb21lLmJpZy50eHQuZmlsZS50eHQbWzBtCgkbWzk3bWlucHV0OiAbWzBtG1szODs1OzI1MG1GG1swbSAbWzk3bSAgICA4YhtbMG0gG1s5NW0vbW50L2NvbXBlbmRpdW0vRGV2TGFiL2RleHZlcnQvdGVzdC9maWxlcxtbMG0bWzk2bS8bWzBtG1s5NW1zdWJEaXIvdHh0LmIbWzBtCgkbWzk3bWlucHV0OiAbWzBtG1szODs1OzkzbUQbWzBtIBtbOTdtICAgICAgG1swbSAbWzk1bS9tbnQvY29tcGVuZGl1bS9EZXZMYWIvZGV4dmVydC90ZXN0L2ZpbGVzG1swbRtbOTZtLxtbMG0bWzk1bXN1YkRpci9tb3JlX3N1Yi90aGlyZBtbMG0KCRtbOTdtb3RoZXI6IBtbMG0bWzk2bUwbWzBtIBtbOTdtICAgICAgG1swbSAbWzk1bS9tbnQvY29tcGVuZGl1bS9EZXZMYWIvZGV4dmVydC90ZXN0L2ZpbGVzG1swbRtbOTZtLxtbMG0bWzk1bXN1YkRpci9zeW1saW5rRmlsZRtbMG0KCRtbOTdtb3RoZXI6IBtbMG0bWzM4OzU7MjUwbUYbWzBtIBtbOTdtICAgMTBiG1swbSAbWzk1bS9tbnQvY29tcGVuZGl1bS9EZXZMYWIvZGV4dmVydC90ZXN0L2ZpbGVzG1swbRtbOTZtLxtbMG0bWzk1bXN1YkRpci9tb3JlX3N1Yi9jLnR4dBtbMG0=");	// eslint-disable-line max-len
});

Deno.test("removeType", async () =>
{
	const a = await FileSet.create("/mnt/compendium/DevLab/dexvert/test/files", "input", [
		"/mnt/compendium/DevLab/dexvert/test/files/some.big.txt.file.txt",
		"/mnt/compendium/DevLab/dexvert/test/files/subDir/txt.b",
		"/mnt/compendium/DevLab/dexvert/test/files/subDir/more_sub/third"]);
	await a.addAll("other", ["/mnt/compendium/DevLab/dexvert/test/files/subDir/symlinkFile", "/mnt/compendium/DevLab/dexvert/test/files/subDir/more_sub/c.txt"]);
	assertStrictEquals(a.files.input.length, 3);
	assertStrictEquals(a.files.other.length, 2);
	assert(a.files.input);
	assert(a.files.other);
	assertStrictEquals(a.all.length, 5);
	a.removeType("other");
	assertStrictEquals(a.files.input.length, 3);
	assert(!a.files.other);
	assert(a.files.input);
	assertStrictEquals(a.all.length, 3);
	a.removeType("input");
	assertStrictEquals(a.all.length, 0);
});

Deno.test("changeType", async () =>
{
	const a = await FileSet.create("/mnt/compendium/DevLab/dexvert/test/files", "input", [
		"/mnt/compendium/DevLab/dexvert/test/files/some.big.txt.file.txt",
		"/mnt/compendium/DevLab/dexvert/test/files/subDir/txt.b",
		"/mnt/compendium/DevLab/dexvert/test/files/subDir/more_sub/third"]);
	await a.addAll("other", ["/mnt/compendium/DevLab/dexvert/test/files/subDir/symlinkFile", "/mnt/compendium/DevLab/dexvert/test/files/subDir/more_sub/c.txt"]);
	assertStrictEquals(a.files.input.length, 3);
	assertStrictEquals(a.files.other.length, 2);
	assert(a.files.input);
	assert(a.files.other);
	assertStrictEquals(a.all.length, 5);
	a.changeType("other", "bingo");
	assertStrictEquals(a.files.input.length, 3);
	assert(!a.files.other);
	assert(a.files.input);
	assert(a.files.bingo.length, 2);
	assertStrictEquals(a.all.length, 5);
	a.changeType("bingo", "input");
	assertStrictEquals(a.files.input.length, 5);
	assert(!a.files.other);
	assert(!a.files.bingo);
	assert(a.files.input);
	assertStrictEquals(a.all.length, 5);
});

Deno.test("rsyncTo", async () =>
{
	let a = await FileSet.create("/mnt/compendium/DevLab/dexvert/test/files", "input", [
		"/mnt/compendium/DevLab/dexvert/test/files/some.big.txt.file.txt",
		"/mnt/compendium/DevLab/dexvert/test/files/subDir/txt.b",
		"/mnt/compendium/DevLab/dexvert/test/files/subDir/more_sub/third"]);
	await a.addAll("other", ["/mnt/compendium/DevLab/dexvert/test/files/subDir/symlinkFile", "/mnt/compendium/DevLab/dexvert/test/files/subDir/more_sub/c.txt"]);

	const tmpDirPath = await fileUtil.genTempPath();
	await Deno.mkdir(tmpDirPath);
	await a.rsyncTo(tmpDirPath);
	assert([
		"some.big.txt.file.txt",
		"subDir",
		"subDir/symlinkFile",
		"subDir/txt.b",
		"subDir/more_sub",
		"subDir/more_sub/c.txt",
		"subDir/more_sub/third"].map(v => path.join(tmpDirPath, v)).includesAll(await fileUtil.tree(tmpDirPath)));
	await fileUtil.unlink(tmpDirPath, {recursive : true});

	await Deno.mkdir(tmpDirPath);
	let b = await a.rsyncTo(tmpDirPath, {type : "other"});
	assertEquals(await fileUtil.tree(tmpDirPath), [
		"subDir",
		"subDir/symlinkFile",
		"subDir/more_sub",
		"subDir/more_sub/c.txt"].map(v => path.join(tmpDirPath, v)));
	assert(!b.files.input);
	assertStrictEquals(b.files.other.length, 2);
	assertStrictEquals(b.all.length, 2);
	await fileUtil.unlink(tmpDirPath, {recursive : true});

	await Deno.mkdir(tmpDirPath);
	b = await a.rsyncTo(tmpDirPath, {type : "other", relativeFrom : "/mnt/compendium/DevLab/dexvert/test/files/subDir"});
	assertEquals(await fileUtil.tree(tmpDirPath), [
		"symlinkFile",
		"more_sub",
		"more_sub/c.txt"].map(v => path.join(tmpDirPath, v)));
	await fileUtil.unlink(tmpDirPath, {recursive : true});
	assertStrictEquals(b.other.rel, "symlinkFile");
	assertStrictEquals(b.other.isSymlink, true);

	// dir file
	a = await FileSet.create("/mnt/compendium/DevLab/dexvert/test/files", "input", [
		"/mnt/compendium/DevLab/dexvert/test/files/some.big.txt.file.txt",
		"/mnt/compendium/DevLab/dexvert/test/files/subDir"]);
	await Deno.mkdir(tmpDirPath);
	b = await a.rsyncTo(tmpDirPath);
	const bStat = await Deno.stat(path.join(tmpDirPath, "subDir", "more_sub", "c.txt"));
	assertStrictEquals(bStat.size, 10);
	await fileUtil.unlink(tmpDirPath, {recursive : true});
});

Deno.test("serialize", async () =>
{
	const a = await FileSet.create("/mnt/compendium/DevLab/dexvert/test/files", "input", [
		"/mnt/compendium/DevLab/dexvert/test/files/some.big.txt.file.txt",
		"/mnt/compendium/DevLab/dexvert/test/files/subDir/txt.b",
		"/mnt/compendium/DevLab/dexvert/test/files/subDir/more_sub/third"]);
	await a.addAll("other", ["/mnt/compendium/DevLab/dexvert/test/files/subDir/symlinkFile", "/mnt/compendium/DevLab/dexvert/test/files/subDir/more_sub/c.txt"]);

	assertStrictEquals(JSON.stringify(a.serialize()), fileSetJSON);
});

Deno.test("remove", async () =>
{
	const a = await FileSet.create("/mnt/compendium/DevLab/dexvert/test/files", "input", [
		"/mnt/compendium/DevLab/dexvert/test/files/some.big.txt.file.txt",
		"/mnt/compendium/DevLab/dexvert/test/files/subDir/txt.b",
		"/mnt/compendium/DevLab/dexvert/test/files/subDir/more_sub/third"]);
	assertStrictEquals(a.all.length, 3);
	a.remove("input", await DexFile.create("/mnt/compendium/DevLab/dexvert/test/files/subDir/txt.b"));
	assertStrictEquals(a.all.length, 2);
	a.remove("input", await DexFile.create("/mnt/compendium/DevLab/dexvert/test/files/subDir/txt.b"));
	a.remove("wrongType", await DexFile.create("/mnt/compendium/DevLab/dexvert/test/files/some.big.txt.file.txt"));
	assertStrictEquals(a.all.length, 2);
});

