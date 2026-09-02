package com.Hatsune.Midi;

import javax.sound.midi.*;

class Senbonzakura2 {
    //Midi键盘
    private static final int A0  = 21;
    private static final int Bb0 = 22;
    private static final int B0  = 23;

    private static final int C1  = 24;
    private static final int Db1 = 25;
    private static final int D1  = 26;
    private static final int Eb1 = 27;
    private static final int E1  = 28;
    private static final int F1  = 29;
    private static final int Gb1 = 30;
    private static final int G1  = 31;
    private static final int Ab1 = 32;
    private static final int A1  = 33;
    private static final int Bb1 = 34;
    private static final int B1  = 35;

    private static final int C2  = 36;
    private static final int Db2 = 37;
    private static final int D2  = 38;
    private static final int Eb2 = 39;
    private static final int E2  = 40;
    private static final int F2  = 41;
    private static final int Gb2 = 42;
    private static final int G2  = 43;
    private static final int Ab2 = 44;
    private static final int A2  = 45;
    private static final int Bb2 = 46;
    private static final int B2  = 47;

    private static final int C3  = 48;
    private static final int Db3 = 49;
    private static final int D3  = 50;
    private static final int Eb3 = 51;
    private static final int E3  = 52;
    private static final int F3  = 53;
    private static final int Gb3 = 54;
    private static final int G3  = 55;
    private static final int Ab3 = 56;
    private static final int A3  = 57;
    private static final int Bb3 = 58;
    private static final int B3  = 59;

    private static final int C4  = 60;
    private static final int Db4 = 61;
    private static final int D4  = 62;
    private static final int Eb4 = 63;
    private static final int E4  = 64;
    private static final int F4  = 65;
    private static final int Gb4 = 66;
    private static final int G4  = 67;
    private static final int Ab4 = 68;
    private static final int A4  = 69;
    private static final int Bb4 = 70;
    private static final int B4  = 71;

    private static final int C5  = 72;
    private static final int Db5 = 73;
    private static final int D5  = 74;
    private static final int Eb5 = 75;
    private static final int E5  = 76;
    private static final int F5  = 77;
    private static final int Gb5 = 78;
    private static final int G5  = 79;
    private static final int Ab5 = 80;
    private static final int A5  = 81;
    private static final int Bb5 = 82;
    private static final int B5  = 83;

    private static final int C6  = 84;
    private static final int Db6 = 85;
    private static final int D6  = 86;
    private static final int Eb6 = 87;
    private static final int E6  = 88;
    private static final int F6  = 89;
    private static final int Gb6 = 90;
    private static final int G6  = 91;
    private static final int Ab6 = 92;
    private static final int A6  = 93;
    private static final int Bb6 = 94;
    private static final int B6  = 95;

    private static final int C7  = 96;
    private static final int Db7 = 97;
    private static final int D7  = 98;
    private static final int Eb7 = 99;
    private static final int E7  = 100;
    private static final int F7  = 101;
    private static final int Gb7 = 102;
    private static final int G7  = 103;
    private static final int Ab7 = 104;
    private static final int A7  = 105;
    private static final int Bb7 = 106;
    private static final int B7  = 107;

    private static final int C8  = 108;

    private static final int REST = 0;

    private static final int second = 60;   //三十二分音符
    private static final int sixth = 120;   //十六分音符
    private static final int eighth = 240;   //八分音符
    private static final int fourth = 360;   //浮点八分音符
    private static final int quarter = 480;  //四分音符
    private static final int third = 720;   //浮点四分音符
    private static final int twice = 960;   //二分音符

    public static void play(Track track, int note, long tick, int duration) {
        if (note != REST) {
            try {
                track.add(new MidiEvent(new ShortMessage(ShortMessage.NOTE_ON, 0, note, 88), tick));
                track.add(new MidiEvent(new ShortMessage(ShortMessage.NOTE_OFF, 0, note, 0), tick + duration));
            } catch (InvalidMidiDataException e) {
                e.printStackTrace();
            }
        }
    }


    public static void main(String[] args) throws InvalidMidiDataException, InterruptedException, MidiUnavailableException {
        int resolution = 480;
        Sequence sequence = new Sequence(Sequence.PPQ, resolution);
        Track trackRight = sequence.createTrack(); // 右手轨道
        Track trackLeft  = sequence.createTrack(); // 左手轨道
        long tick = 0;
        long tick2 = 0;

        //格式：音符,时长,音符,时长……
        int[] accompScore = {
                D3, eighth, REST, sixth, D3, eighth, REST, sixth, D3, eighth,
                D3, eighth, REST, sixth, D3, eighth, REST, sixth, D3, eighth,
                D3, eighth, REST, sixth, D3, eighth, REST, sixth, D3, eighth,
                D3, eighth, REST, eighth, D3, eighth, REST, eighth,
                D3, eighth, REST, sixth, D3, eighth, REST, sixth, D3, eighth,
                D3, eighth, REST, sixth, D3, eighth, REST, sixth, D3, eighth,
                D3, eighth, REST, eighth, D3, eighth, REST, eighth, C3, eighth, REST, eighth, C3, eighth, REST, eighth,


                Bb2, eighth, Bb3, eighth, Bb2, eighth, Bb3, eighth, C3, eighth, C4, eighth,  C3, eighth, C4, eighth,
                D3, eighth, D4, eighth, D3, eighth, D4, eighth,  D3, eighth, D4, eighth, D3, eighth, D4, eighth,
                Bb2, eighth, Bb3, eighth, Bb2, eighth, Bb3, eighth, C3, eighth, C4, eighth,  C3, eighth, C4, eighth,
                D3, eighth, D4, eighth, D3, eighth, D4, eighth,  D3, eighth, D4, eighth, D3, eighth, D4, eighth,

                Bb2, eighth, Bb3, eighth, Bb2, eighth, Bb3, eighth, C3, eighth, C4, eighth,  C3, eighth, C4, eighth,
                D3, eighth, D4, eighth, D3, eighth, D4, eighth,  D3, eighth, D4, eighth, D3, eighth, D4, eighth,
                Bb2, eighth, Bb3, eighth, Bb2, eighth, Bb3, eighth, C3, eighth, C4, eighth,  C3, eighth, C4, eighth,
                D3, eighth, D4, eighth, D3, eighth, D4, eighth,  D3, eighth, D4, eighth, D3, eighth, D4, eighth,

                Bb2, eighth, Bb3, eighth, Bb2, eighth, Bb3, eighth, C3, eighth, C4, eighth,  C3, eighth, C4, eighth,
                D3, eighth, D4, eighth, D3, eighth, D4, eighth,  D3, eighth, D4, eighth, D3, eighth, D4, eighth,
                Bb2, eighth, Bb3, eighth, Bb2, eighth, Bb3, eighth, C3, eighth, C4, eighth,  C3, eighth, C4, eighth,
                D3, eighth, D4, eighth, D3, eighth, D4, eighth,  D3, eighth, D4, eighth, D3, eighth, D4, eighth,

                Bb2, eighth, Bb3, eighth, Bb2, eighth, Bb3, eighth, C3, eighth, C4, eighth,  C3, eighth, C4, eighth,
                D3, eighth, D4, eighth, D3, eighth, D4, eighth,  D3, eighth, D4, eighth, D3, eighth, D4, eighth,
                Bb2, eighth, Bb3, eighth, Bb2, eighth, Bb3, eighth, C3, eighth, C4, eighth,  C3, eighth, C4, eighth,
                D3, eighth, D4, eighth, D3, eighth, D4, eighth,  D3, eighth, D4, eighth, D3, eighth, D4, eighth,

                D3, eighth, D4, eighth, D3, eighth, D4, eighth, D3, eighth, D4, eighth, D3, eighth, D4, eighth,
                Bb2, eighth, Bb3, eighth, Bb2, eighth, Bb3, eighth, C3, eighth, C4, eighth,  C3, eighth, C4, eighth,
                D3, eighth, D4, eighth, D3, eighth, D4, eighth, D3, eighth, D4, eighth, D3, eighth, D4, eighth,
                Bb2, eighth, Bb3, eighth, Bb2, eighth, Bb3, eighth, C3, eighth, C4, eighth,  C3, eighth, C4, eighth,

                D3, eighth, D4, eighth, D3, eighth, D4, eighth, D3, eighth, D4, eighth, D3, eighth, D4, eighth,
                Bb2, eighth, Bb3, eighth, Bb2, eighth, Bb3, eighth, C3, eighth, C4, eighth,  C3, eighth, C4, eighth,
                D3, eighth, D4, eighth, D3, eighth, D4, eighth, D3, eighth, D4, eighth, D3, eighth, D4, eighth,
                Bb2, eighth, Bb3, eighth, Bb2, eighth, Bb3, eighth, C3, eighth, C4, eighth,  C3, eighth, C4, eighth,

                Bb2, eighth, Bb3, eighth, Bb2, eighth, Bb3, eighth, Bb2, eighth, Bb3, eighth, Bb2, eighth, Bb3, eighth,
                F2, eighth, F3, eighth, F2, eighth, F3, eighth, F2, eighth, F3, eighth, F2, eighth, F3, eighth,
                Bb2, eighth, Bb3, eighth, Bb2, eighth, Bb3, eighth, C3, eighth, C4, eighth,  C3, eighth, C4, eighth,
                D3, eighth, D4, eighth, D3, eighth, D4, eighth, D3, eighth, D4, eighth, D3, eighth, D4, eighth,

                Bb2, eighth, Bb3, eighth, Bb2, eighth, Bb3, eighth, Bb2, eighth, Bb3, eighth, Bb2, eighth, Bb3, eighth,
                F2, eighth, F3, eighth, F2, eighth, F3, eighth, F2, eighth, F3, eighth, F2, eighth, F3, eighth,
                Bb2, eighth, Bb3, eighth, Bb2, eighth, Bb3, eighth, C3, eighth, C4, eighth,  C3, eighth, C4, eighth,
                A2, eighth, A3, eighth, A2, eighth, A3, eighth, Db3, eighth, REST, quarter, REST, eighth,

                D3, eighth, D4, eighth, D3, eighth, D4, eighth, Bb2, eighth, Bb3, eighth, Bb2, eighth, Bb3, eighth,
                C3, eighth, C4, eighth,  C3, eighth, C4, eighth, F3, eighth, F4, eighth, F3, eighth, F4, eighth,
                D3, eighth, D4, eighth, D3, eighth, D4, eighth, Bb2, eighth, Bb3, eighth, Bb2, eighth, Bb3, eighth,
                C3, eighth, C4, eighth,  C3, eighth, C4, eighth, F3, eighth, F4, eighth, F3, eighth, F4, eighth,

                D3, eighth, D4, eighth, D3, eighth, D4, eighth, Bb2, eighth, Bb3, eighth, Bb2, eighth, Bb3, eighth,
                C3, eighth, C4, eighth,  C3, eighth, C4, eighth, F3, eighth, F4, eighth, F3, eighth, F4, eighth,
                D3, eighth, D4, eighth, D3, eighth, D4, eighth, Bb2, eighth, Bb3, eighth, Bb2, eighth, Bb3, eighth,
                C3, eighth, C4, eighth,  C3, eighth, C4, eighth, D3, eighth, D4, eighth, D3, eighth, D4, eighth,

                D3, eighth, D4, eighth, D3, eighth, D4, eighth, Bb2, eighth, Bb3, eighth, Bb2, eighth, Bb3, eighth,
                C3, eighth, C4, eighth,  C3, eighth, C4, eighth, F3, eighth, F4, eighth, F3, eighth, F4, eighth,
                D3, eighth, D4, eighth, D3, eighth, D4, eighth, Bb2, eighth, Bb3, eighth, Bb2, eighth, Bb3, eighth,
                C3, eighth, C4, eighth,  C3, eighth, C4, eighth, F3, eighth, F4, eighth, F3, eighth, F4, eighth,

                D3, eighth, D4, eighth, D3, eighth, D4, eighth, Bb2, eighth, Bb3, eighth, Bb2, eighth, Bb3, eighth,
                C3, eighth, C4, eighth,  C3, eighth, C4, eighth, F3, eighth, F4, eighth, F3, eighth, F4, eighth,
                D3, eighth, D4, eighth, D3, eighth, D4, eighth, Bb2, eighth, Bb3, eighth, Bb2, eighth, Bb3, eighth,
                C3, eighth, C4, eighth,  C3, eighth, C4, eighth, D3, eighth, D4, eighth, D3, eighth, D4, eighth,


                Bb2, eighth, Bb3, eighth, Bb2, eighth, Bb3, eighth, C3, eighth, C4, eighth,  C3, eighth, C4, eighth,
                D3, eighth, D4, eighth, D3, eighth, D4, eighth,  D3, eighth, D4, eighth, D3, eighth, D4, eighth,
                Bb2, eighth, Bb3, eighth, Bb2, eighth, Bb3, eighth, C3, eighth, C4, eighth,  C3, eighth, C4, eighth,
                D3, eighth, D4, eighth, D3, eighth, D4, eighth,  D3, eighth, D4, eighth, D3, eighth, D4, eighth,

                Bb2, eighth, Bb3, eighth, Bb2, eighth, Bb3, eighth, C3, eighth, C4, eighth,  C3, eighth, C4, eighth,
                D3, eighth, D4, eighth, D3, eighth, D4, eighth,  D3, eighth, D4, eighth, D3, eighth, D4, eighth,
                Bb2, eighth, Bb3, eighth, Bb2, eighth, Bb3, eighth, C3, eighth, C4, eighth,  C3, eighth, C4, eighth,
                D3, eighth, D4, eighth, D3, eighth, D4, eighth,  D3, eighth, D4, eighth, D3, eighth, D4, eighth,

                D3, eighth, D4, eighth, D3, eighth, D4, eighth, D3, eighth, D4, eighth, D3, eighth, D4, eighth,
                Bb2, eighth, Bb3, eighth, Bb2, eighth, Bb3, eighth, C3, eighth, C4, eighth,  C3, eighth, C4, eighth,
                D3, eighth, D4, eighth, D3, eighth, D4, eighth, D3, eighth, D4, eighth, D3, eighth, D4, eighth,
                Bb2, eighth, Bb3, eighth, Bb2, eighth, Bb3, eighth, C3, eighth, C4, eighth,  C3, eighth, C4, eighth,

                D3, eighth, D4, eighth, D3, eighth, D4, eighth, D3, eighth, D4, eighth, D3, eighth, D4, eighth,
                Bb2, eighth, Bb3, eighth, Bb2, eighth, Bb3, eighth, C3, eighth, C4, eighth,  C3, eighth, C4, eighth,
                D3, eighth, D4, eighth, D3, eighth, D4, eighth, D3, eighth, D4, eighth, D3, eighth, D4, eighth,
                Bb2, eighth, Bb3, eighth, Bb2, eighth, Bb3, eighth, C3, eighth, C4, eighth,  C3, eighth, C4, eighth,

                Bb2, eighth, Bb3, eighth, Bb2, eighth, Bb3, eighth, Bb2, eighth, Bb3, eighth, Bb2, eighth, Bb3, eighth,
                F2, eighth, F3, eighth, F2, eighth, F3, eighth, F2, eighth, F3, eighth, F2, eighth, F3, eighth,
                Bb2, eighth, Bb3, eighth, Bb2, eighth, Bb3, eighth, C3, eighth, C4, eighth,  C3, eighth, C4, eighth,
                D3, eighth, D4, eighth, D3, eighth, D4, eighth, D3, eighth, D4, eighth, D3, eighth, D4, eighth,

                Bb2, eighth, Bb3, eighth, Bb2, eighth, Bb3, eighth, Bb2, eighth, Bb3, eighth, Bb2, eighth, Bb3, eighth,
                F2, eighth, F3, eighth, F2, eighth, F3, eighth, F2, eighth, F3, eighth, F2, eighth, F3, eighth,
                Bb2, eighth, Bb3, eighth, Bb2, eighth, Bb3, eighth, C3, eighth, C4, eighth,  C3, eighth, C4, eighth,
                A2, eighth, A3, eighth, A2, eighth, A3, eighth, Db3, eighth, REST, quarter, REST, eighth,

                D3, eighth, D4, eighth, D3, eighth, D4, eighth, Bb2, eighth, Bb3, eighth, Bb2, eighth, Bb3, eighth,
                C3, eighth, C4, eighth,  C3, eighth, C4, eighth, F3, eighth, F4, eighth, F3, eighth, F4, eighth,
                D3, eighth, D4, eighth, D3, eighth, D4, eighth, Bb2, eighth, Bb3, eighth, Bb2, eighth, Bb3, eighth,
                C3, eighth, C4, eighth,  C3, eighth, C4, eighth, F3, eighth, F4, eighth, F3, eighth, F4, eighth,

                D3, eighth, D4, eighth, D3, eighth, D4, eighth, Bb2, eighth, Bb3, eighth, Bb2, eighth, Bb3, eighth,
                C3, eighth, C4, eighth,  C3, eighth, C4, eighth, F3, eighth, F4, eighth, F3, eighth, F4, eighth,
                D3, eighth, D4, eighth, D3, eighth, D4, eighth, Bb2, eighth, Bb3, eighth, Bb2, eighth, Bb3, eighth,
                C3, eighth, C4, eighth,  C3, eighth, C4, eighth, D3, eighth, D4, eighth, D3, eighth, D4, eighth,

                D3, eighth, D4, eighth, D3, eighth, D4, eighth, Bb2, eighth, Bb3, eighth, Bb2, eighth, Bb3, eighth,
                C3, eighth, C4, eighth,  C3, eighth, C4, eighth, F3, eighth, F4, eighth, F3, eighth, F4, eighth,
                D3, eighth, D4, eighth, D3, eighth, D4, eighth, Bb2, eighth, Bb3, eighth, Bb2, eighth, Bb3, eighth,
                C3, eighth, C4, eighth,  C3, eighth, C4, eighth, F3, eighth, F4, eighth, F3, eighth, F4, eighth,

                D3, eighth, D4, eighth, D3, eighth, D4, eighth, Bb2, eighth, Bb3, eighth, Bb2, eighth, Bb3, eighth,
                C3, eighth, C4, eighth,  C3, eighth, C4, eighth, F3, eighth, F4, eighth, F3, eighth, F4, eighth,
                D3, eighth, D4, eighth, D3, eighth, D4, eighth, Bb2, eighth, Bb3, eighth, Bb2, eighth, Bb3, eighth,
                C3, eighth, C4, eighth,  C3, eighth, C4, eighth, D3, eighth, D4, eighth, D3, eighth, D4, eighth,


                D3, twice, Bb2, twice, C3, twice, A2, twice,
                D3, twice, Bb2, twice, C3, twice, A2, twice,

                D3, quarter, D3, quarter, D3, quarter, D3, quarter,
                Bb2, quarter, Bb2, quarter, Bb2, quarter, Bb2, quarter,
                Bb2, quarter, Bb2, quarter, Bb2, quarter, Bb2, quarter,
                C3, quarter, C3, quarter, A2, quarter, A2, quarter,
                D3, quarter, D3, quarter, D3, quarter, D3, quarter,
                Bb2, quarter, Bb2, quarter, Bb2, quarter, Bb2, quarter,
                G2, quarter, G2, quarter, G2, quarter, G2, quarter,
                C2, quarter, C2, quarter, A2, quarter, A2, quarter,
                Bb2, quarter, Bb2, quarter, C3, quarter, C3, quarter,
                A2, quarter, A2, quarter, A2, quarter, A2, quarter,
                Bb2, quarter, Bb2, quarter, C3, quarter, C3, quarter,
                A2, quarter, A2, quarter, A2, quarter, A2, quarter,
                Bb2, quarter, Bb2, quarter, C3, quarter, C3, quarter,
                D3, quarter, D3, quarter, D3, quarter, D3, quarter,
                Bb2, quarter, Bb2, quarter, C3, quarter, C3, quarter,
                A2, quarter, A2, quarter, A2, quarter, A2, quarter,


                Bb2, eighth, Bb3, eighth, Bb2, eighth, Bb3, eighth, Bb2, eighth, Bb3, eighth, Bb2, eighth, Bb3, eighth,
                F2, eighth, F3, eighth, F2, eighth, F3, eighth, F2, eighth, F3, eighth, F2, eighth, F3, eighth,
                Bb2, eighth, Bb3, eighth, Bb2, eighth, Bb3, eighth, C3, eighth, C4, eighth,  C3, eighth, C4, eighth,
                D3, eighth, D4, eighth, D3, eighth, D4, eighth, D3, eighth, D4, eighth, D3, eighth, D4, eighth,

                Bb2, eighth, Bb3, eighth, Bb2, eighth, Bb3, eighth, Bb2, eighth, Bb3, eighth, Bb2, eighth, Bb3, eighth,
                F2, eighth, F3, eighth, F2, eighth, F3, eighth, F2, eighth, F3, eighth, F2, eighth, F3, eighth,
                Bb2, eighth, Bb3, eighth, Bb2, eighth, Bb3, eighth, C3, eighth, C4, eighth, C3, eighth, C4, eighth,
                A2, eighth, A3, eighth, A2, eighth, A3, eighth, Db3, eighth, REST, quarter, REST, eighth,

                D4, twice, Bb3, twice, C4, twice, F4, twice, D4, twice, Bb3, twice, C4, twice, F4, twice,
                D4, twice, Bb3, twice, C4, twice, F4, twice, D4, twice, Bb3, twice, C4, twice, C4, twice,

                E3, eighth, E4, eighth, E3, eighth, E4, eighth, C3, eighth, C4, eighth, C3, eighth, C4, eighth,
                D3, eighth, D4, eighth, D3, eighth, D4, eighth, G3, eighth, G4, eighth, G3, eighth, G4, eighth,
                E3, eighth, E4, eighth, E3, eighth, E4, eighth, C3, eighth, C4, eighth, C3, eighth, C4, eighth,
                D3, eighth, D4, eighth, D3, eighth, D4, eighth, G3, eighth, G4, eighth, G3, eighth, G4, eighth,

                E3, eighth, E4, eighth, E3, eighth, E4, eighth, C3, eighth, C4, eighth, C3, eighth, C4, eighth,
                D3, eighth, D4, eighth, D3, eighth, D4, eighth, G3, eighth, G4, eighth, G3, eighth, G4, eighth,
                E3, eighth, E4, eighth, E3, eighth, E4, eighth, C3, eighth, C4, eighth, C3, eighth, C4, eighth,
                D3, eighth, D4, eighth, D3, eighth, D4, eighth, E3, eighth, E4, eighth, E3, eighth, E4, eighth,

                C3, eighth, C4, eighth, C3, eighth, C4, eighth, D3, eighth, D4, eighth, D3, eighth, D4, eighth,
                E3, eighth, E4, eighth, E3, eighth, E4, eighth, E3, eighth, E4, eighth, E3, eighth, E4, eighth,
                C3, eighth, C4, eighth, C3, eighth, C4, eighth, D3, eighth, D4, eighth, D3, eighth, D4, eighth,
                E3, eighth, E4, eighth, E3, eighth, E4, eighth, E3, eighth, E4, eighth, E3, eighth, E4, eighth,

                C3, eighth, C4, eighth, C3, eighth, C4, eighth, D3, eighth, D4, eighth, D3, eighth, D4, eighth,
                E3, eighth, E4, eighth, E3, eighth, E4, eighth, E3, eighth, E4, eighth, E3, eighth, E4, eighth,
                C3, eighth, C4, eighth, C3, eighth, C4, eighth, D3, eighth, D4, eighth, D3, eighth, D4, eighth,
                E3, eighth, E4, eighth, E3, eighth, E4, eighth, E3, eighth, E4, eighth, E3, eighth, E4, eighth,

                C3, eighth, C4, eighth, C3, eighth, C4, eighth, D3, eighth, D4, eighth, D3, eighth, D4, eighth,
                E3, eighth, E4, eighth, E3, eighth, E4, eighth, E3, eighth, E4, eighth, E3, eighth, E4, eighth,
                C3, eighth, C4, eighth, C3, eighth, C4, eighth, D3, eighth, D4, eighth, D3, eighth, D4, eighth,
                E3, eighth, E4, eighth, E3, eighth, E4, eighth, E3, eighth, E4, eighth, E3, eighth, E4, eighth,

                C3, eighth, C4, eighth, C3, eighth, C4, eighth, D3, eighth, D4, eighth, D3, eighth, D4, eighth,
                E3, eighth, E4, eighth, E3, eighth, E4, eighth, E3, eighth, E4, eighth, E3, eighth, E4, eighth,
                C3, eighth, C4, eighth, C3, eighth, C4, eighth, D3, eighth, D4, eighth, D3, eighth, D4, eighth,
                E3, eighth, E4, eighth, E3, eighth, E4, eighth, E3, eighth, E4, eighth, E3, eighth, E4, eighth,
                E3, eighth, REST, sixth, E3, eighth, REST, sixth, D3, eighth, E3, eighth, REST, eighth,
                E2, quarter,
        };

        int[] melodyScore = {
                D5, eighth, REST, sixth, D5, eighth, REST, sixth, C5,eighth,
                D5, eighth, REST, sixth, D5, eighth, REST, sixth, C5,eighth,
                D5, eighth, REST, sixth, D5, eighth, REST, sixth, C5,eighth,
                D5, eighth, REST, eighth, F5, eighth, REST, eighth,
                D5, eighth, REST, sixth, D5, eighth, REST, sixth, C5,eighth,
                D5, eighth, REST, sixth, D5, eighth, REST, sixth, C5,eighth,
                D5, eighth, REST, eighth, F5, eighth, REST, eighth, G5, eighth, REST, eighth, A5, eighth, REST, eighth,


                G5, eighth, A5, eighth, D5, sixth, C5, sixth, D5, sixth, C5, sixth,
                G5, eighth, A5, eighth, D5, sixth, C5, sixth, D5, sixth, C5, sixth,
                G5, eighth, A5, eighth, D5, sixth, C5, sixth, D5, sixth, C5, sixth,
                F5, eighth, E5, eighth, D5, eighth, C5, eighth,

                G5, eighth, A5, eighth, D5, sixth, C5, sixth, D5, sixth, C5, sixth,
                G5, eighth, A5, eighth, D5, sixth, C5, sixth, D5, sixth, C5, sixth,
                G5, eighth, A5, eighth, C6, eighth, F6, eighth, E6, sixth, F6, sixth, E6, sixth, D6, sixth, C6, eighth, A5, eighth,

                G5, eighth, A5, eighth, D5, sixth, C5, sixth, D5, sixth, C5, sixth,
                G5, eighth, A5, eighth, D5, sixth, C5, sixth, D5, sixth, C5, sixth,
                G5, eighth, A5, eighth, D5, sixth, C5, sixth, D5, sixth, C5, sixth,
                F5, eighth, E5, eighth, D5, eighth, C5, eighth,

                D5, eighth, C5, sixth, D5, sixth, F5, eighth, D5, sixth, F5, sixth, G5, eighth,
                G5, sixth, A5, sixth, C6, sixth, F6, sixth, A5, sixth, C6, sixth, F6, eighth,
                E6, eighth, D6, eighth, C6, eighth, D6, eighth,

                C6, eighth, D6, eighth, F6, eighth,

                G6, eighth, A6, eighth, D6, sixth, C6, sixth, D6, sixth, C6, sixth,
                G6, eighth, A6, eighth, D6, sixth, C6, sixth, D6, sixth, C6, sixth,
                G6, eighth, A6, eighth, D6, sixth, C6, sixth, D6, sixth, C6, sixth,
                F6, eighth, E6, eighth, D6, eighth, C6, eighth,

                G6, eighth, A6, eighth, D6, sixth, C6, sixth, D6, sixth, C6, sixth,
                G6, eighth, A6, eighth, D6, sixth, C6, sixth, D6, sixth, C6, sixth,
                G6, eighth, A6, eighth, C7, eighth, F7, eighth, E7, sixth, F7, sixth, E7, sixth, D7, sixth, C7, eighth, A6, eighth,

                G6, eighth, A6, eighth, D6, sixth, C6, sixth, D6, sixth, C6, sixth,
                G6, eighth, A6, eighth, D6, sixth, C6, sixth, D6, sixth, C6, sixth,
                G6, eighth, A6, eighth, D6, sixth, C6, sixth, D6, sixth, C6, sixth,
                F6, eighth, E6, eighth, D6, eighth, C6, eighth,

                A6, sixth, G6, sixth, A6, sixth, C7, sixth,
                D7, sixth, C7, sixth, A6, sixth, G6, sixth,
                D6, eighth, F6, eighth, G6, eighth, A6, eighth,
                D6, eighth, REST, sixth, D6, eighth, REST, sixth, C6, eighth, D6, eighth, REST, quarter, REST, eighth,

                D5, eighth, REST, eighth, D5, eighth, REST, second, C5,sixth, REST, second, D5, eighth, F5, eighth, F5, eighth, G5, eighth,
                D5, eighth, REST, eighth, D5, eighth, REST, second, C5,sixth, REST, second, D5, eighth, C5, eighth, A4, eighth, C5, eighth,
                D5, eighth, REST, eighth, D5, eighth, REST, second, C5,sixth, REST, second, D5, eighth, F5, eighth, G5, eighth, A5, eighth,
                A5, eighth, REST, eighth, G5, sixth, A5, sixth, G5, sixth, REST, sixth, F5, eighth, REST, eighth, D5, eighth, REST, eighth,

                D5, eighth, REST, eighth, D5, eighth, REST, second, C5,sixth, REST, second, D5, eighth, F5, eighth, F5, eighth, G5, eighth,
                D5, eighth, REST, eighth, D5, eighth, REST, second, C5,sixth, REST, second, D5, eighth, C5, eighth, A4, eighth, C5, eighth,
                D5, eighth, REST, eighth, D5, eighth, REST, second, C5,sixth, REST, second, D5, eighth, F5, eighth, G5, eighth, A5, eighth,
                A5, eighth, REST, eighth, G5, sixth, A5, sixth, G5, sixth, REST, sixth, F5, eighth, REST, eighth, D5, eighth, REST, eighth,

                F5, eighth, REST, eighth, E5, eighth, REST, eighth, D5, eighth, REST, eighth, C5, eighth, REST, eighth,
                C5, eighth, C5, sixth, D5, sixth, A4, eighth, G4, eighth, A4, eighth, REST, quarter, REST, eighth,
                A4, eighth, C5, eighth, D5, eighth, REST, eighth, G5, eighth, REST, eighth, E5, eighth, REST, eighth,
                F5, eighth, REST, eighth,E5, sixth, REST, sixth, C5, eighth, D5, eighth, REST, quarter, REST, eighth,

                F5, eighth, REST, eighth, E5, eighth, REST, eighth, D5, eighth, REST, eighth, C5, eighth, REST, eighth,
                C5, eighth, C5, sixth, D5, sixth, A4, eighth, G4, eighth, A4, eighth, REST, eighth,
                A4, eighth, C5, eighth, D5, eighth, D5, eighth, REST, eighth, D5, eighth, F5, quarter, G5, quarter, E5, quarter,
                REST, quarter, REST, quarter,

                D5, eighth, F5, eighth, G5, eighth, REST, sixth, G5, eighth, REST, sixth, A5, eighth, A5, eighth,
                REST, eighth, REST, eighth,
                A5, eighth, C6, eighth, D6, eighth, G5, eighth, F5, eighth, A5, eighth, REST, eighth,
                D5, eighth, F5, eighth, G5, eighth, REST, sixth, G5, eighth, REST, sixth, A5, eighth, A5, eighth,
                REST, eighth, REST, eighth,
                A5, eighth, Bb5, eighth, A5, eighth, G5, eighth, F5, eighth, F5, eighth, REST, eighth,

                D5, eighth, F5, eighth, G5, eighth, REST, sixth, G5, eighth, REST, sixth, A5, eighth, A5, eighth,
                REST, eighth, REST, eighth,
                A5, eighth, C6, eighth, D6, eighth, G5, eighth, F5, eighth, A5, eighth, REST, eighth,
                D5, eighth, F5, eighth, Bb5, quarter, A5, quarter, G5, quarter, F5, quarter,
                G5, eighth, A5, eighth, E5, eighth, C5, eighth, D5, eighth, REST, eighth,

                D5, eighth, F5, eighth, G5, eighth, REST, sixth, G5, eighth, REST, sixth, A5, eighth, A5, eighth,
                REST, eighth, REST, eighth,
                A5, eighth, C6, eighth, D6, eighth, G5, eighth, F5, eighth, A5, eighth, REST, eighth,
                D5, eighth, F5, eighth, G5, eighth, REST, sixth, G5, eighth, REST, sixth, A5, eighth, A5, eighth,
                REST, eighth, REST, eighth,
                A5, eighth, Bb5, eighth, A5, eighth, G5, eighth, F5, eighth, F5, eighth, REST, eighth,

                D5, eighth, F5, eighth, G5, eighth, REST, sixth, G5, eighth, REST, sixth, A5, eighth, A5, eighth,
                REST, eighth, REST, eighth,
                A5, eighth, C6, eighth, D6, eighth, G5, eighth, F5, eighth, A5, eighth, REST, eighth,
                D5, eighth, F5, eighth, Bb5, quarter, A5, quarter, G5, quarter, F5, quarter,
                G5, eighth, F5, eighth, A5, eighth, C6, eighth, D6, eighth, REST, quarter, REST, eighth,


                G5, eighth, A5, eighth, D5, sixth, C5, sixth, D5, sixth, C5, sixth,
                G5, eighth, A5, eighth, D5, sixth, C5, sixth, D5, sixth, C5, sixth,
                G5, eighth, A5, eighth, D5, sixth, C5, sixth, D5, sixth, C5, sixth,
                F5, eighth, E5, eighth, D5, eighth, C5, eighth,

                G5, eighth, A5, eighth, D5, sixth, C5, sixth, D5, sixth, C5, sixth,
                G5, eighth, A5, eighth, D5, sixth, C5, sixth, D5, sixth, C5, sixth,
                G5, eighth, A5, eighth, C6, eighth, F6, eighth, E6, sixth, F6, sixth, E6, sixth, D6, sixth, C6, eighth, A5, eighth,

                G5, eighth, A5, eighth, D5, sixth, C5, sixth, D5, sixth, C5, sixth,
                G5, eighth, A5, eighth, D5, sixth, C5, sixth, D5, sixth, C5, sixth,
                G5, eighth, A5, eighth, D5, sixth, C5, sixth, D5, sixth, C5, sixth,
                F5, eighth, E5, eighth, D5, eighth, C5, eighth,

                A5, sixth, G5, sixth, A5, sixth, C6, sixth,
                D6, sixth, C6, sixth, A5, sixth, G5, sixth,
                D5, eighth, F5, eighth, G5, eighth, A5, eighth,
                D5, eighth, REST, sixth, D5, eighth, REST, sixth, C5, eighth, D5, eighth, REST, quarter, REST, eighth,

                D5, eighth, REST, eighth, D5, eighth, REST, second, C5,sixth, REST, second, D5, eighth, F5, eighth, F5, eighth, G5, eighth,
                D5, eighth, REST, eighth, D5, eighth, REST, second, C5,sixth, REST, second, D5, eighth, C5, eighth, A4, eighth, C5, eighth,
                D5, eighth, REST, eighth, D5, eighth, REST, second, C5,sixth, REST, second, D5, eighth, F5, eighth, G5, eighth, A5, eighth,
                A5, eighth, REST, eighth, G5, sixth, A5, sixth, G5, sixth, REST, sixth, F5, eighth, REST, eighth, D5, eighth, REST, eighth,

                D5, eighth, REST, eighth, D5, eighth, REST, second, C5,sixth, REST, second, D5, eighth, F5, eighth, F5, eighth, G5, eighth,
                D5, eighth, REST, eighth, D5, eighth, REST, second, C5,sixth, REST, second, D5, eighth, C5, eighth, A4, eighth, C5, eighth,
                D5, eighth, REST, eighth, D5, eighth, REST, second, C5,sixth, REST, second, D5, eighth, F5, eighth, G5, eighth, A5, eighth,
                A5, eighth, REST, eighth, G5, sixth, A5, sixth, G5, sixth, REST, sixth, F5, eighth, REST, eighth, D5, eighth, REST, eighth,

                F5, eighth, REST, eighth, E5, eighth, REST, eighth, D5, eighth, REST, eighth, C5, eighth, REST, eighth,
                C5, eighth, C5, sixth, D5, sixth, A4, eighth, G4, eighth, A4, eighth, REST, quarter, REST, eighth,
                A4, eighth, C5, eighth, D5, eighth, REST, eighth, G5, eighth, REST, eighth, E5, eighth, REST, eighth,
                F5, eighth, REST, eighth,E5, sixth, REST, sixth, C5, eighth, D5, eighth, REST, quarter, REST, eighth,

                F5, eighth, REST, eighth, E5, eighth, REST, eighth, D5, eighth, REST, eighth, C5, eighth, REST, eighth,
                C5, eighth, C5, sixth, D5, sixth, A4, eighth, G4, eighth, A4, eighth, REST, eighth,
                A4, eighth, C5, eighth, D5, eighth, D5, eighth, REST, eighth, D5, eighth, F5, quarter, G5, quarter, E5, quarter,
                REST, quarter, REST, quarter,

                D5, eighth, F5, eighth, G5, eighth, REST, sixth, G5, eighth, REST, sixth, A5, eighth, A5, eighth,
                REST, eighth, REST, eighth,
                A5, eighth, C6, eighth, D6, eighth, G5, eighth, F5, eighth, A5, eighth, REST, eighth,
                D5, eighth, F5, eighth, G5, eighth, REST, sixth, G5, eighth, REST, sixth, A5, eighth, A5, eighth,
                REST, eighth, REST, eighth,
                A5, eighth, Bb5, eighth, A5, eighth, G5, eighth, F5, eighth, F5, eighth, REST, eighth,

                D5, eighth, F5, eighth, G5, eighth, REST, sixth, G5, eighth, REST, sixth, A5, eighth, A5, eighth,
                REST, eighth, REST, eighth,
                A5, eighth, C6, eighth, D6, eighth, G5, eighth, F5, eighth, A5, eighth, REST, eighth,
                D5, eighth, F5, eighth, Bb5, quarter, A5, quarter, G5, quarter, F5, quarter,
                G5, eighth, A5, eighth, E5, eighth, C5, eighth, D5, eighth, REST, eighth,

                D5, eighth, F5, eighth, G5, eighth, REST, sixth, G5, eighth, REST, sixth, A5, eighth, A5, eighth,
                REST, eighth, REST, eighth,
                A5, eighth, C6, eighth, D6, eighth, G5, eighth, F5, eighth, A5, eighth, REST, eighth,
                D5, eighth, F5, eighth, G5, eighth, REST, sixth, G5, eighth, REST, sixth, A5, eighth, A5, eighth,
                REST, eighth, REST, eighth,
                A5, eighth, Bb5, eighth, A5, eighth, G5, eighth, F5, eighth, F5, eighth, REST, eighth,

                D5, eighth, F5, eighth, G5, eighth, REST, sixth, G5, eighth, REST, sixth, A5, eighth, A5, eighth,
                REST, eighth, REST, eighth,
                A5, eighth, C6, eighth, D6, eighth, G5, eighth, F5, eighth, A5, eighth, REST, eighth,
                D5, eighth, F5, eighth, Bb5, quarter, A5, quarter, G5, quarter, F5, quarter,
                G5, eighth, F5, eighth, A5, eighth, C6, eighth, D6, eighth, REST, fourth, REST, fourth,


                D6, eighth, D6, eighth, D6, eighth, D6, eighth, D6, eighth, D6, eighth, D6,sixth, C6, sixth, A5, sixth, REST, sixth,
                G5, eighth, G5, eighth, G5, eighth, G5, eighth, G5, eighth, G5, eighth, G5,sixth, F5, sixth, D5, sixth, REST, sixth,
                D5, eighth, D5, eighth, D5, eighth, D5, eighth, D5, eighth, D5, eighth, D5,sixth, C5, sixth, A4, sixth, REST, sixth,
                G4, eighth, A4, sixth, G4, sixth, A4, sixth, C5, sixth, D5, sixth, F5, sixth, A5, sixth, C6, sixth, D6, sixth, F6, sixth, E6, sixth, REST,sixth,

                D5, sixth, F5, sixth,
                A5, sixth, F5, sixth, D5, sixth, A5, sixth, A5, sixth, F5, sixth, D5, sixth, A5, sixth,
                A5, sixth, F5, sixth, D5, sixth, A5, sixth, A5, sixth, F5, sixth, D5, sixth, A5, sixth,
                Bb5, sixth, G5, sixth, F5, sixth, Bb5, sixth, Bb5, sixth, G5, sixth, F5, sixth, Bb5, sixth,
                Bb5, sixth, G5, sixth, F5, sixth, Bb5, sixth,  Bb5, sixth, G5, sixth, F5, sixth, Bb5, sixth,
                Bb5, sixth, F5, sixth, D5, sixth, Bb5, sixth, Bb5, sixth, F5, sixth, D5, sixth, Bb5, sixth,
                Bb5, sixth, F5, sixth, D5, sixth, Bb5, sixth, Bb5, sixth, F5, sixth, D5, sixth, Bb5, sixth,
                G5, sixth, E5, sixth, C5, sixth, G5, sixth, G5, sixth, E5, sixth, C5, sixth, E5, sixth,
                A5, sixth, F5, sixth, D5, sixth, A5, sixth, A5, sixth, F5, sixth, D5, sixth, E5, sixth,
                A5, sixth, F5, sixth, D5, sixth, A5, sixth, D6, sixth, A5, sixth, F5, sixth, D5, sixth,
                G5, sixth, F5, sixth, D5, sixth, A5, sixth, F6, sixth, D6, sixth, A5, sixth, F5, sixth,
                Bb5, sixth, F5, sixth, D5, sixth, Bb5, sixth, D6, sixth, Bb5, sixth, F5, sixth, D5, sixth,
                Bb5, sixth, F5, sixth, D5, sixth, Bb5, sixth, F6, sixth, E6, sixth, D6, sixth, Bb5, sixth,
                D6, sixth, Bb5, sixth, F5, sixth, Bb5, sixth, F6, sixth, Bb5, sixth, D6, sixth, F6, sixth,
                Bb6, sixth, F6, sixth, D6, sixth, Bb5, sixth, Bb5, sixth, G5, sixth, D5, sixth, Bb4, sixth,
                C5, quarter, C4, sixth, E4,sixth, G4, sixth, C5, sixth,
                Db5, quarter, Db4, sixth, F4, sixth, Ab4, sixth, D5, sixth,
                G5, sixth, A5, sixth, F5, sixth, A5, sixth, G5, sixth, F5, sixth, E5, sixth, D5, sixth,
                E5, sixth, D5, sixth, C5, sixth, D5, sixth, D5, sixth, C5, sixth, A4, sixth, G4, sixth,
                A4, sixth, G4, sixth, F4, sixth, A4, sixth, G4, sixth, F4, sixth, E4, sixth, F4, sixth, D4, twice,
                D4, eighth, E4, eighth, F4, eighth, A4, eighth,
                G4, sixth, A4, sixth, D5, sixth, E5, sixth, F5, sixth, E5, sixth, D5, sixth, F5, sixth,
                A5, third, C6, eighth, A5, twice,
                D4, eighth, C4, eighth, G4, eighth, F4, eighth, A4, eighth, G4, eighth, D5, eighth, C5, eighth,
                G5, eighth, F5, eighth, C6, sixth, A5, sixth, C6, sixth, A5, sixth, C6, twice,
                F5, eighth, D5, sixth, Bb4, sixth, F4, sixth, Bb4, sixth, D5, sixth, F5, sixth,
                G5, eighth, E5, sixth, C5, sixth, G4, sixth, C5, sixth, E5, sixth, G5, sixth,
                A5, fourth, Ab5, fourth, A5, sixth, Ab5, sixth, A5, twice,

                F5, eighth, REST, eighth, E5, eighth, REST, eighth, D5, eighth, REST, eighth, C5, eighth, REST, eighth,
                C5, eighth, C5, sixth, D5, sixth, A4, eighth, G4, eighth, A4, eighth, REST, quarter, REST, eighth,
                A4, eighth, C5, eighth, D5, eighth, REST, eighth, G5, eighth, REST, eighth, E5, eighth, REST, eighth,
                F5, eighth, REST, eighth,E5, sixth, REST, sixth, C5, eighth, D5, eighth, REST, quarter, REST, eighth,

                F5, eighth, REST, eighth, E5, eighth, REST, eighth, D5, eighth, REST, eighth, C5, eighth, REST, eighth,
                C5, eighth, C5, sixth, D5, sixth, A4, eighth, G4, eighth, A4, eighth, REST, eighth,
                A4, eighth, C5, eighth, D5, eighth, D5, eighth, REST, eighth, D5, eighth, F5, quarter, G5, quarter, E5, quarter,
                REST, quarter, REST, quarter,

                D5, eighth, F5, eighth, G5, eighth, REST, sixth, G5, eighth, REST, sixth, A5, eighth, A5, eighth,
                REST, eighth, REST, eighth,
                A5, eighth, C6, eighth, D6, eighth, G5, eighth, F5, eighth, A5, eighth, REST, eighth,
                D5, eighth, F5, eighth, G5, eighth, REST, sixth, G5, eighth, REST, sixth, A5, eighth, A5, eighth,
                REST, eighth, REST, eighth,
                A5, eighth, Bb5, eighth, A5, eighth, G5, eighth, F5, eighth, F5, eighth, REST, eighth,

                D5, eighth, F5, eighth, G5, eighth, REST, sixth, G5, eighth, REST, sixth, A5, eighth, A5, eighth,
                REST, eighth, REST, eighth,
                A5, eighth, C6, eighth, D6, eighth, G5, eighth, F5, eighth, A5, eighth, REST, eighth,
                D5, eighth, F5, eighth, Bb5, quarter, A5, quarter, G5, quarter, F5, quarter,
                G5, eighth, A5, eighth, G5, eighth, A5, eighth, A5, eighth, REST, eighth,

                E5, eighth, G5, eighth, A5, eighth, REST, sixth, A5, eighth, REST, sixth, B5, eighth, B5, eighth,
                REST, eighth, REST, eighth,
                B5, eighth, D6, eighth, E6, eighth, A5, eighth, G5, eighth, B5, eighth, REST, eighth,
                E5, eighth, G5, eighth, A5, eighth, REST, sixth, A5, eighth, REST, sixth, B5, eighth, B5, eighth,
                REST, eighth, REST, eighth,
                B5, eighth, C6, eighth, B5, eighth, A5, eighth, G5, eighth, G5, eighth, REST, eighth,

                E5, eighth, G5, eighth, A5, eighth, REST, sixth, A5, eighth, REST, sixth, B5, eighth, B5, eighth,
                REST, eighth, REST, eighth,
                B5, eighth, D6, eighth, E6, eighth, A5, eighth, G5, eighth, B5, eighth, REST, eighth,
                E5, eighth, G5, eighth, C6, quarter, B5, quarter, A5, quarter, G5, quarter,
                A5, eighth, G5, eighth, B5, eighth, D6, eighth, E6, eighth, REST, eighth, E5, eighth, G5, eighth,

                A5, eighth, B5, eighth, E5, sixth, D5, sixth, E5, sixth, D5, sixth,
                A5, eighth, B5, eighth, E5, sixth, D5, sixth, E5, sixth, D5, sixth,
                A5, eighth, B5, eighth, E5, sixth, D5, sixth, E5, sixth, D5, sixth,
                G5, eighth, Gb5, eighth, E5, eighth, D5, eighth,

                A5, eighth, B5, eighth, E5, sixth, D5, sixth, E5, sixth, D5, sixth,
                A5, eighth, B5, eighth, E5, sixth, D5, sixth, E5, sixth, D5, sixth,
                A5, eighth, B5, eighth, D6, eighth, G6, eighth, Gb6, sixth, G6, sixth, Gb6, sixth, E6, sixth, D6, eighth, B5, eighth,

                A5, eighth, B5, eighth, E5, sixth, D5, sixth, E5, sixth, D5, sixth,
                A5, eighth, B5, eighth, E5, sixth, D5, sixth, E5, sixth, D5, sixth,
                A5, eighth, B5, eighth, E5, sixth, D5, sixth, E5, sixth, D5, sixth,
                G5, eighth, Gb5, eighth, E5, eighth, D5, eighth,

                E5, eighth, D5, sixth, E5, sixth, G5, eighth, E5, sixth, G5, sixth, A5, eighth,
                A5, sixth, B5, sixth, D6, sixth, G6, sixth, B5, sixth, D6, sixth, G6, eighth,
                Gb6, eighth, E6, eighth, D6, eighth, E6, eighth,

                D6, eighth, E6, eighth, G6, eighth,

                A6, eighth, B6, eighth, E6, sixth, D6, sixth, E6, sixth, D6, sixth,
                A6, eighth, B6, eighth, E6, sixth, D6, sixth, E6, sixth, D6, sixth,
                A6, eighth, B6, eighth, E6, sixth, D6, sixth, E6, sixth, D6, sixth,
                G6, eighth, Gb6, eighth, E6, eighth, D6, eighth,

                A6, eighth, B6, eighth, E6, sixth, D6, sixth, E6, sixth, D6, sixth,
                A6, eighth, B6, eighth, E6, sixth, D6, sixth, E6, sixth, D6, sixth,
                A6, eighth, B6, eighth, D7, eighth, G7, eighth, Gb7, sixth, G7, sixth, Gb7, sixth, E7, sixth, D7, eighth, B6, eighth,

                A6, eighth, B6, eighth, E6, sixth, D6, sixth, E6, sixth, D6, sixth,
                A6, eighth, B6, eighth, E6, sixth, D6, sixth, E6, sixth, D6, sixth,
                A6, eighth, B6, eighth, E6, sixth, D6, sixth, E6, sixth, D6, sixth,
                G6, eighth, Gb6, eighth, E6, eighth, D6, eighth,

                B6, sixth, A6, sixth, B6, sixth, D7, sixth,
                E7, sixth, D7, sixth, B6, sixth, A6, sixth,
                E6, eighth, G6, eighth, A6, eighth, B6, eighth,
                E6, eighth, REST, sixth, E6, eighth, REST, sixth, D6, eighth, E6, eighth, REST, quarter, REST, eighth,
                E6, eighth, REST, sixth, E6, eighth, REST, sixth, D6, eighth, E6, eighth, REST, eighth, E3, quarter,

        };

        for(int i = 0; i < melodyScore.length; i += 2){
            int note = melodyScore[i];
            int dur = melodyScore[i+1];
            play(trackRight, note, tick, dur);
            tick += dur;
        }

        for(int i = 0; i < accompScore.length; i += 2){
            int note = accompScore[i];
            int dur = accompScore[i+1];
            play(trackLeft, note, tick2, dur);
            tick2 += dur;
        }

        Sequencer sequencer = MidiSystem.getSequencer();
        sequencer.open();
        sequencer.setSequence(sequence);
        sequencer.setTempoInBPM(150); //BPN
        sequencer.start();

        Thread.sleep(248000);
        sequencer.stop();
        sequencer.close();
    }
}
