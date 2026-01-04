#!/usr/bin/env node
/* eslint-disable */
// AI VIBE CODED by Gemini 3 Flash Preview
const fs = require('fs');
const MidiWriter = require('midi-writer-js');

if (process.argv.length < 4) {
    console.log("Usage: node mmf2mid.js <input.json> <output.mid>");
    process.exit(1);
}

const inputPath = process.argv[2];
const outputPath = process.argv[3];
const smafData = JSON.parse(fs.readFileSync(inputPath, 'utf8'));

const trackChunks = smafData.sub_chunks.filter(c => 
    c.chunk_header && c.chunk_header.signature.startsWith("MTR")
);

const midiTracks = [];

trackChunks.forEach((mtrChunk, trackIdx) => {
    const midiTrack = new MidiWriter.Track();
    const mtsq = mtrChunk.sub_chunks.find(s => 
        s.chunk_header && s.chunk_header.signature.startsWith("Mtsq")
    );

    if (!mtsq || !mtsq.events) return;

    midiTrack.addTrackName(`MTR Track ${trackIdx}`);

    let absoluteTick = 0;
    const channelOctaveShift = new Array(16).fill(0);
    
    // Track CC7 (Volume) and CC11 (Expression) to calculate a balanced velocity
    const channelVolume = new Array(16).fill(100);
    const channelExpression = new Array(16).fill(127);

    mtsq.events.forEach((item) => {
        absoluteTick += (item.duration || 0);
        const event = item.event;
        if (!event) return;

        const chan = (event.channel !== undefined) ? event.channel : 0;
        // Shift each MTR chunk to its own set of channels to prevent conflicts
        const midiChan = (chan + (trackIdx * 4)) % 16 + 1;

        // 1. OCTAVE SHIFT (Standalone Value Events)
        if (event.value !== undefined && event.note === undefined && event.pc === undefined && event.cc === undefined) {
            channelOctaveShift[chan] = event.value * 12;
            return;
        }

        // 2. PROGRAM CHANGE
        if (event.pc !== undefined) {
            midiTrack.addEvent(new MidiWriter.ProgramChangeEvent({
                instrument: event.pc,
                channel: midiChan,
                tick: absoluteTick
            }));
        }

        // 3. CONTROLLER CHANGE (Volume/Expression)
        if (event.cc !== undefined) {
            if (event.cc === 7) channelVolume[chan] = event.value;
            if (event.cc === 11) channelExpression[chan] = event.value;

            midiTrack.addEvent(new MidiWriter.ControllerChangeEvent({
                controllerNumber: event.cc,
                controllerValue: event.value,
                channel: midiChan,
                tick: absoluteTick
            }));
        }

        // 4. NOTE EVENTS
        if (event.note !== undefined) {
            const pitch = Math.max(0, Math.min(127, event.note + channelOctaveShift[chan]));
            
            // BALANCE LOGIC: 
            // Calculated Velocity = (Base Velocity) * (Expression/127)
            // This ensures the background "alternating notes" follow the fade-outs
            let baseVel = event.velocity || 90;
            let dynamicVel = Math.floor(baseVel * (channelExpression[chan] / 127));
            
            // Boost the melody track (usually PC 66 Sax or first MTR chunk)
            if (event.pc === 66 || trackIdx === 1) {
                dynamicVel = Math.min(127, dynamicVel + 25);
            }

            midiTrack.addEvent(new MidiWriter.NoteEvent({
                pitch: pitch,
                velocity: dynamicVel,
                duration: 'T' + Math.max(1, event.gate_time),
                channel: midiChan,
                tick: absoluteTick
            }));
        }
    });

    midiTracks.push(midiTrack);
});

const write = new MidiWriter.Writer(midiTracks);
fs.writeFileSync(outputPath, write.buildFile());
console.log(`MIDI saved: ${outputPath}`);