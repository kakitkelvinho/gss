# Expert lab recipe (seed 1)

By-product of the reference run: what the scripted expert did, in order, with lab time.

- Parts bought: DL-C25 delay stage, BBO-T236 crystal, 4 x MIR-1 mirror, 1 x PER-1 periscope (EUR 4800; C_min = EUR 1900)
- Lab time: 150.6 min of 240 (62.8%), 110 tool calls
- Result: eta = 0.9948, R = 0.9118, O = 0.9966, |dt| = 2.9 fs

| # | t (min) | tool | args |
|---|---|---|---|
| 0 | 5.0 | read_manual | `{"device": "table"}` |
| 1 | 10.0 | read_manual | `{"device": "opa"}` |
| 2 | 15.0 | read_manual | `{"device": "delay_stage"}` |
| 3 | 20.0 | read_manual | `{"device": "sample_mount"}` |
| 4 | 35.0 | buy | `{"items": {"DL-C25": 1, "BBO-T236": 1, "MIR-1": 4, "PER-1": 1}}` |
| 5 | 40.1 | place | `{"part": "sample", "x": 1300.0, "z": 600.0, "height": 120.0, "yaw_deg": 180.0}` |
| 6 | 40.2 | unblock | `{"arm": "probe"}` |
| 7 | 45.4 | place | `{"part": "periscope-1", "x": 2050.0, "z": 935.0, "height": 120.0, "yaw_deg": 180.0, "height_in": 158.0}` |
| 8 | 45.9 | ir_card | `{"x": 1700.0, "z": 935.0, "height": 120.0}` |
| 9 | 46.4 | ir_card | `{"x": 1700.0, "z": 935.0, "height": 120.0}` |
| 10 | 46.9 | knob | `{"part": "periscope-1", "axis": "yaw", "delta_mrad": 8.5714}` |
| 11 | 47.4 | ir_card | `{"x": 1700.0, "z": 935.0, "height": 120.0}` |
| 12 | 47.9 | knob | `{"part": "periscope-1", "axis": "pitch", "delta_mrad": 8.5714}` |
| 13 | 48.4 | ir_card | `{"x": 1700.0, "z": 935.0, "height": 120.0}` |
| 14 | 48.9 | knob | `{"part": "periscope-1", "axis": "yaw", "delta_mrad": -10.6547}` |
| 15 | 49.4 | knob | `{"part": "periscope-1", "axis": "pitch", "delta_mrad": -8.9081}` |
| 16 | 49.9 | ir_card | `{"x": 1700.0, "z": 935.0, "height": 120.0}` |
| 17 | 50.5 | knob | `{"part": "periscope-1", "axis": "yaw", "delta_mrad": -1.2906}` |
| 18 | 51.0 | knob | `{"part": "periscope-1", "axis": "pitch", "delta_mrad": -1.0311}` |
| 19 | 51.5 | ir_card | `{"x": 1700.0, "z": 935.0, "height": 120.0}` |
| 20 | 56.5 | place | `{"part": "mirror-1", "x": 1700.0, "z": 935.0, "height": 120.0, "yaw_deg": -45.0}` |
| 21 | 57.1 | ir_card | `{"x": 1700.0, "z": 592.0, "height": 120.0}` |
| 22 | 57.6 | ir_card | `{"x": 1700.0, "z": 592.0, "height": 120.0}` |
| 23 | 58.2 | knob | `{"part": "mirror-1", "axis": "yaw", "delta_mrad": 8.7464}` |
| 24 | 58.8 | ir_card | `{"x": 1700.0, "z": 592.0, "height": 120.0}` |
| 25 | 59.5 | knob | `{"part": "mirror-1", "axis": "pitch", "delta_mrad": 8.7464}` |
| 26 | 60.1 | ir_card | `{"x": 1700.0, "z": 592.0, "height": 120.0}` |
| 27 | 60.7 | knob | `{"part": "mirror-1", "axis": "yaw", "delta_mrad": 6.382}` |
| 28 | 61.2 | knob | `{"part": "mirror-1", "axis": "pitch", "delta_mrad": -10.1343}` |
| 29 | 61.9 | ir_card | `{"x": 1700.0, "z": 592.0, "height": 120.0}` |
| 30 | 62.5 | knob | `{"part": "mirror-1", "axis": "yaw", "delta_mrad": 0.6498}` |
| 31 | 63.0 | knob | `{"part": "mirror-1", "axis": "pitch", "delta_mrad": 0.8471}` |
| 32 | 63.6 | ir_card | `{"x": 1700.0, "z": 592.0, "height": 120.0}` |
| 33 | 68.6 | place | `{"part": "mirror-2", "x": 1700.0, "z": 592.0, "height": 120.0, "yaw_deg": 135.0}` |
| 34 | 69.1 | ir_card | `{"x": 1300.0, "z": 592.0, "height": 120.0}` |
| 35 | 69.6 | ir_card | `{"x": 1300.0, "z": 592.0, "height": 120.0}` |
| 36 | 70.1 | knob | `{"part": "mirror-2", "axis": "yaw", "delta_mrad": 7.5}` |
| 37 | 70.6 | ir_card | `{"x": 1300.0, "z": 592.0, "height": 120.0}` |
| 38 | 71.2 | knob | `{"part": "mirror-2", "axis": "pitch", "delta_mrad": 7.5}` |
| 39 | 71.7 | ir_card | `{"x": 1300.0, "z": 592.0, "height": 120.0}` |
| 40 | 72.2 | knob | `{"part": "mirror-2", "axis": "yaw", "delta_mrad": 5.5781}` |
| 41 | 72.7 | knob | `{"part": "mirror-2", "axis": "pitch", "delta_mrad": -8.4833}` |
| 42 | 73.2 | ir_card | `{"x": 1300.0, "z": 592.0, "height": 120.0}` |
| 43 | 73.7 | knob | `{"part": "mirror-2", "axis": "yaw", "delta_mrad": -0.4708}` |
| 44 | 74.2 | knob | `{"part": "mirror-2", "axis": "pitch", "delta_mrad": -1.0548}` |
| 45 | 74.7 | ir_card | `{"x": 1300.0, "z": 592.0, "height": 120.0}` |
| 46 | 75.2 | knob | `{"part": "mirror-2", "axis": "yaw", "delta_mrad": -0.0536}` |
| 47 | 75.7 | knob | `{"part": "mirror-2", "axis": "pitch", "delta_mrad": 1.0191}` |
| 48 | 76.3 | ir_card | `{"x": 1300.0, "z": 592.0, "height": 120.0}` |
| 49 | 76.8 | knob | `{"part": "mirror-2", "axis": "yaw", "delta_mrad": 0.3069}` |
| 50 | 77.3 | knob | `{"part": "mirror-2", "axis": "pitch", "delta_mrad": -0.8313}` |
| 51 | 77.8 | ir_card | `{"x": 1300.0, "z": 592.0, "height": 120.0}` |
| 52 | 77.9 | unblock | `{"arm": "pump"}` |
| 53 | 83.0 | place | `{"part": "stage", "x": 781.5, "z": 309.0, "height": 120.0, "yaw_deg": 180.0}` |
| 54 | 83.5 | ir_card | `{"x": 1500.0, "z": 324.0, "height": 120.0}` |
| 55 | 88.5 | place | `{"part": "mirror-3", "x": 1500.0, "z": 325.9, "height": 119.1, "yaw_deg": 135.0}` |
| 56 | 89.2 | ir_card | `{"x": 1500.0, "z": 608.0, "height": 120.0}` |
| 57 | 89.7 | ir_card | `{"x": 1500.0, "z": 608.0, "height": 120.0}` |
| 58 | 90.3 | knob | `{"part": "mirror-3", "axis": "yaw", "delta_mrad": 10.6345}` |
| 59 | 91.0 | ir_card | `{"x": 1500.0, "z": 608.0, "height": 120.0}` |
| 60 | 91.6 | knob | `{"part": "mirror-3", "axis": "pitch", "delta_mrad": 10.6345}` |
| 61 | 92.2 | ir_card | `{"x": 1500.0, "z": 608.0, "height": 120.0}` |
| 62 | 92.9 | knob | `{"part": "mirror-3", "axis": "yaw", "delta_mrad": -12.5365}` |
| 63 | 93.4 | knob | `{"part": "mirror-3", "axis": "pitch", "delta_mrad": -10.3206}` |
| 64 | 94.0 | ir_card | `{"x": 1500.0, "z": 608.0, "height": 120.0}` |
| 65 | 94.7 | knob | `{"part": "mirror-3", "axis": "yaw", "delta_mrad": -0.7922}` |
| 66 | 95.2 | knob | `{"part": "mirror-3", "axis": "pitch", "delta_mrad": -1.3527}` |
| 67 | 95.8 | ir_card | `{"x": 1500.0, "z": 608.0, "height": 120.0}` |
| 68 | 100.8 | place | `{"part": "mirror-4", "x": 1500.0, "z": 608.0, "height": 120.0, "yaw_deg": 225.0}` |
| 69 | 101.3 | ir_card | `{"x": 1300.0, "z": 608.0, "height": 120.0}` |
| 70 | 101.8 | ir_card | `{"x": 1300.0, "z": 608.0, "height": 120.0}` |
| 71 | 102.3 | knob | `{"part": "mirror-4", "axis": "yaw", "delta_mrad": 15.0}` |
| 72 | 102.8 | ir_card | `{"x": 1300.0, "z": 608.0, "height": 120.0}` |
| 73 | 103.3 | knob | `{"part": "mirror-4", "axis": "pitch", "delta_mrad": 15.0}` |
| 74 | 103.8 | ir_card | `{"x": 1300.0, "z": 608.0, "height": 120.0}` |
| 75 | 104.3 | knob | `{"part": "mirror-4", "axis": "yaw", "delta_mrad": -8.4178}` |
| 76 | 104.8 | knob | `{"part": "mirror-4", "axis": "pitch", "delta_mrad": -15.183}` |
| 77 | 105.3 | ir_card | `{"x": 1300.0, "z": 608.0, "height": 120.0}` |
| 78 | 105.5 | block | `{"arm": "pump"}` |
| 79 | 105.7 | view_camera | `{"plane": "sample"}` |
| 80 | 105.8 | unblock | `{"arm": "pump"}` |
| 81 | 105.9 | view_camera | `{"plane": "sample"}` |
| 82 | 106.1 | view_camera | `{"plane": "sample"}` |
| 83 | 106.7 | knob | `{"part": "mirror-4", "axis": "yaw", "delta_mrad": 0.3}` |
| 84 | 106.9 | view_camera | `{"plane": "sample"}` |
| 85 | 107.1 | view_camera | `{"plane": "sample"}` |
| 86 | 107.7 | knob | `{"part": "mirror-4", "axis": "pitch", "delta_mrad": 0.3}` |
| 87 | 108.0 | view_camera | `{"plane": "sample"}` |
| 88 | 108.1 | view_camera | `{"plane": "sample"}` |
| 89 | 108.7 | knob | `{"part": "mirror-4", "axis": "yaw", "delta_mrad": 4.2769}` |
| 90 | 109.2 | knob | `{"part": "mirror-4", "axis": "pitch", "delta_mrad": -0.6341}` |
| 91 | 109.5 | view_camera | `{"plane": "sample"}` |
| 92 | 109.6 | view_camera | `{"plane": "sample"}` |
| 93 | 110.2 | knob | `{"part": "mirror-4", "axis": "yaw", "delta_mrad": 0.1744}` |
| 94 | 110.7 | knob | `{"part": "mirror-4", "axis": "pitch", "delta_mrad": -0.288}` |
| 95 | 111.0 | view_camera | `{"plane": "sample"}` |
| 96 | 111.1 | view_camera | `{"plane": "sample"}` |
| 97 | 111.7 | knob | `{"part": "mirror-4", "axis": "yaw", "delta_mrad": 0.0107}` |
| 98 | 112.2 | knob | `{"part": "mirror-4", "axis": "pitch", "delta_mrad": -0.0161}` |
| 99 | 112.5 | view_camera | `{"plane": "sample"}` |
| 100 | 112.7 | view_camera | `{"plane": "sample"}` |
| 101 | 115.7 | measure_path | `{"arm": "pump"}` |
| 102 | 118.7 | measure_path | `{"arm": "probe"}` |
| 103 | 118.7 | status | `{}` |
| 104 | 146.9 | scan | `{"start_mm": 7.4, "end_mm": 19.4, "step_mm": 0.005, "t_int": 0.4}` |
| 105 | 150.1 | scan | `{"start_mm": 14.055, "end_mm": 14.135, "step_mm": 0.001, "t_int": 2.0}` |
| 106 | 150.2 | move_stage | `{"position_mm": 14.09539}` |
| 107 | 150.4 | view_camera | `{"plane": "sample"}` |
| 108 | 150.5 | view_camera | `{"plane": "sample"}` |
| 109 | 150.6 | submit | `{}` |
