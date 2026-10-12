/* Vibe coded by Codex
 * Checked Darkhorse decoder, adapted from XADMaster's
 * XADStuffItXDarkhorseHandle.m, CarrylessRangeCoder.m and XADLZSSHandle.m.
 * Copyright (c) 2017-present, MacPaw Way Ltd. All rights reserved.
 * LGPL-2.1-or-later; distributed WITHOUT ANY WARRANTY.
 * See LICENSE-XADMaster.txt.
 * Build: cc -O2 -std=c99 -fPIC -shared sitx_darkhorse.c -o libsitx_darkhorse.so
 */
#include <stddef.h>
#include <stdint.h>

typedef struct {
    const uint8_t *data;
    size_t size, pos;
    uint32_t code, range;
    int error;
} Coder;

typedef struct {
    uint32_t flag[4], secondary_flag;
    uint32_t literal[16][256], predicted_literal[16][256][2];
    uint32_t recency[3], short_recency[4];
    uint32_t length, short_length[4][16], long_length[256];
    uint32_t distance_symbol[4][64], distance[10][32], low_distance[16];
} Model;

static uint8_t read_byte(Coder *coder)
{
    if (coder->pos == coder->size) {
        coder->error = 1;
        return 0;
    }
    return coder->data[coder->pos++];
}

static void normalize(Coder *coder)
{
    if (!coder->range) coder->error = 1;
    while (!coder->error && coder->range < 0x1000000) {
        coder->code = (coder->code << 8) | read_byte(coder);
        coder->range <<= 8;
    }
}

static unsigned weighted_bit(Coder *coder, uint32_t *weight)
{
    if (coder->error) return 0;
    if (coder->code >= coder->range) {
        coder->error = 1;
        return 0;
    }
    uint32_t threshold = (coder->range >> 12) * *weight;
    unsigned bit = coder->code >= threshold;
    if (bit) {
        coder->code -= threshold;
        coder->range -= threshold;
        *weight -= *weight >> 5;
    } else {
        coder->range = threshold;
        *weight += (0x1000 - *weight) >> 5;
    }
    normalize(coder);
    return bit;
}

static unsigned direct_bit(Coder *coder)
{
    if (coder->error) return 0;
    coder->range /= 2;
    if (!coder->range || coder->code / coder->range > 1) {
        coder->error = 1;
        return 0;
    }
    unsigned bit = coder->code / coder->range;
    coder->code -= bit * coder->range;
    normalize(coder);
    return bit;
}

static unsigned symbol(Coder *coder, uint32_t *weights, unsigned bits)
{
    unsigned value = 1;
    for (unsigned i = 0; i < bits; i++)
        value = (value << 1) | weighted_bit(coder, &weights[value]);
    return value - (1u << bits);
}

static void initialize_model(Model *m)
{
    m->secondary_flag = m->length = 0x800;
    for (unsigned i = 0; i < 3; i++) m->recency[i] = 0x800;
    for (unsigned i = 0; i < 4; i++) {
        m->flag[i] = m->short_recency[i] = 0x800;
        for (unsigned j = 0; j < 16; j++) m->short_length[i][j] = 0x800;
        for (unsigned j = 0; j < 64; j++) m->distance_symbol[i][j] = 0x800;
    }
    for (unsigned i = 0; i < 16; i++) {
        m->low_distance[i] = 0x800;
        for (unsigned j = 0; j < 256; j++) {
            m->literal[i][j] = 0x800;
            m->predicted_literal[i][j][0] = 0x800;
            m->predicted_literal[i][j][1] = 0x800;
        }
    }
    for (unsigned i = 0; i < 256; i++) m->long_length[i] = 0x800;
    for (unsigned i = 0; i < 10; i++)
        for (unsigned j = 0; j < 32; j++) m->distance[i][j] = 0x800;
}

static uint8_t literal(Coder *coder, Model *m, uint8_t prev, int guess)
{
    unsigned value = 1, context = prev >> 4;
    if (guess >= 0) {
        unsigned prediction = (unsigned)guess;
        while (value < 256) {
            unsigned predicted_bit = (prediction >> 7) & 1;
            unsigned bit = weighted_bit(coder, &m->predicted_literal[context][value][predicted_bit]);
            value = (value << 1) | bit;
            if (bit != predicted_bit) break;
            prediction <<= 1;
        }
    }
    while (value < 256)
        value = (value << 1) | weighted_bit(coder, &m->literal[context][value]);
    return (uint8_t)value;
}

static unsigned length(Coder *coder, Model *m, unsigned context)
{
    if (!weighted_bit(coder, &m->length))
        return symbol(coder, m->short_length[context], 4) + 2;
    return symbol(coder, m->long_length, 8) + 18;
}

static uint32_t distance(Coder *coder, Model *m, unsigned len)
{
    unsigned context = len - 2;
    if (context > 3) context = 3;
    unsigned sym = symbol(coder, m->distance_symbol[context], 6);
    if (sym < 4) return sym + 1;
    if (sym >= 60) {
        coder->error = 1;
        return 0;
    }
    unsigned bits = sym / 2 - 1;
    uint32_t offset = (2u | (sym & 1)) << bits;
    if (sym < 14) offset += symbol(coder, m->distance[sym - 4], bits);
    else {
        for (unsigned i = bits; i > 4; i--) offset += direct_bit(coder) << (i - 1);
        offset += symbol(coder, m->low_distance, 4);
    }
    return offset + 1;
}

static int recency(Coder *coder, Model *m, unsigned context)
{
    if (!weighted_bit(coder, &m->recency[0]))
        return weighted_bit(coder, &m->short_recency[context]) ? 0 : -1;
    if (!weighted_bit(coder, &m->recency[1])) return 1;
    return weighted_bit(coder, &m->recency[2]) ? 3 : 2;
}

static void update_distances(uint32_t *distances, unsigned index, uint32_t dist)
{
    for (unsigned i = index; i > 0; i--) distances[i] = distances[i - 1];
    distances[0] = dist;
}

static uint8_t history(const uint8_t *output, size_t pos, uint32_t dist)
{
    return dist <= pos ? output[pos - dist] : 0;
}

ptrdiff_t sitx_darkhorse_decompress(const uint8_t *src, size_t src_size,
                                  uint8_t *output, size_t capacity, uint32_t window_size)
{
    if (!src || src_size < 6 || src[0] > 30 || (!output && capacity) ||
            capacity > PTRDIFF_MAX) return -1;
    uint32_t window = 1u << src[0];
    if (window < 0x100000) window = 0x100000;
    if (window_size != window) return -1;

    /* The exponent and the initialization byte are distinct header fields. */
    Coder coder = {src, src_size, 2, 0, UINT32_MAX, 0};
    for (int i = 0; i < 4; i++) coder.code = (coder.code << 8) | read_byte(&coder);
    Model model;
    initialize_model(&model);
    uint32_t distances[4] = {1, 1, 1, 1};
    size_t pos = 0;
    int guess = -1;

    while (!coder.error) {
        unsigned context = pos & 3;
        if (!weighted_bit(&coder, &model.flag[context])) {
            if (pos == capacity) return -1;
            uint8_t byte = literal(&coder, &model, history(output, pos, 1), guess);
            if (coder.error) return -1;
            output[pos++] = byte;
            guess = -1;
        } else {
            unsigned len;
            uint32_t dist;
            if (!weighted_bit(&coder, &model.secondary_flag)) {
                len = length(&coder, &model, context);
                if (coder.error) return -1;
                if (len == 273)
                    return coder.pos == coder.size ? (ptrdiff_t)pos : -1;
                dist = distance(&coder, &model, len);
                update_distances(distances, 3, dist);
            } else {
                int index = recency(&coder, &model, context);
                if (index == -1) { dist = distances[0]; len = 1; }
                else {
                    dist = distances[index];
                    update_distances(distances, (unsigned)index, dist);
                    len = length(&coder, &model, context);
                }
            }
            if (coder.error || !dist || dist > window || len > capacity - pos) return -1;
            guess = history(output, pos, dist - len % dist);
            /* Forward copying is required: matches may overlap their source. */
            for (unsigned i = 0; i < len; i++) {
                uint8_t byte = history(output, pos, dist);
                output[pos++] = byte;
            }
        }
    }
    return -1;
}
