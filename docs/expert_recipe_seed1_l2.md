# Expert lab recipe (seed 1, level 2)

By-product of the reference run: what the scripted expert did, in order, with lab time.

- OPA wavelength 1300 nm. Parts bought: DL-C25 delay stage, 4 x MIR-1 mirror, 1 x PER-1 periscope, CAM-VSWIR, GAP-TPA (EUR 10350; C_min = EUR 7750)
- Lab time: 152.7 min of 240 (63.6%), 115 tool calls
- Result: eta = 0.9815, R = 0.8961, O = 0.9931, |dt| = 20.2 fs

| # | t (min) | tool | args |
|---|---|---|---|
| 0 | 5.0 | read_manual | `{"device": "table"}` |
| 1 | 10.0 | read_manual | `{"device": "opa"}` |
| 2 | 15.0 | read_manual | `{"device": "delay_stage"}` |
| 3 | 20.0 | read_manual | `{"device": "sample_mount"}` |
| 4 | 35.0 | buy | `{"items": {"DL-C25": 1, "MIR-1": 4, "PER-1": 1, "GAP-TPA": 1, "CAM-VSWIR": 1}}` |
| 5 | 40.1 | place | `{"part": "sample", "x": 1200.0, "z": 600.0, "height": 120.0, "yaw_deg": 0.0}` |
| 6 | 40.2 | unblock | `{"arm": "opa"}` |
| 7 | 45.4 | place | `{"part": "periscope-1", "x": 2050.0, "z": 935.0, "height": 120.0, "yaw_deg": 180.0, "height_in": 158.0}` |
| 8 | 45.9 | ir_card | `{"x": 1461.6295090390227, "z": 935.0, "height": 120.0}` |
| 9 | 46.4 | ir_card | `{"x": 1461.6295090390227, "z": 935.0, "height": 120.0}` |
| 10 | 46.9 | knob | `{"part": "periscope-1", "axis": "yaw", "delta_mrad": 5.0988}` |
| 11 | 47.4 | ir_card | `{"x": 1461.6295090390227, "z": 935.0, "height": 120.0}` |
| 12 | 47.9 | knob | `{"part": "periscope-1", "axis": "pitch", "delta_mrad": 5.0988}` |
| 13 | 48.4 | ir_card | `{"x": 1461.6295090390227, "z": 935.0, "height": 120.0}` |
| 14 | 49.0 | knob | `{"part": "periscope-1", "axis": "yaw", "delta_mrad": -7.0432}` |
| 15 | 49.5 | knob | `{"part": "periscope-1", "axis": "pitch", "delta_mrad": -5.5161}` |
| 16 | 50.0 | ir_card | `{"x": 1461.6295090390227, "z": 935.0, "height": 120.0}` |
| 17 | 50.5 | knob | `{"part": "periscope-1", "axis": "yaw", "delta_mrad": -0.7803}` |
| 18 | 51.0 | knob | `{"part": "periscope-1", "axis": "pitch", "delta_mrad": -0.6926}` |
| 19 | 51.5 | ir_card | `{"x": 1461.6295090390227, "z": 935.0, "height": 120.0}` |
| 20 | 56.5 | place | `{"part": "mirror-1", "x": 1461.6295090390227, "z": 935.0, "height": 120.0, "yaw_deg": -45.0}` |
| 21 | 57.0 | ir_card | `{"x": 1461.6295090390227, "z": 861.6295090390227, "height": 120.0}` |
| 22 | 57.5 | ir_card | `{"x": 1461.6295090390227, "z": 861.6295090390227, "height": 120.0}` |
| 23 | 58.0 | knob | `{"part": "mirror-1", "axis": "yaw", "delta_mrad": 40.8884}` |
| 24 | 58.5 | ir_card | `{"x": 1461.6295090390227, "z": 861.6295090390227, "height": 120.0}` |
| 25 | 59.0 | knob | `{"part": "mirror-1", "axis": "pitch", "delta_mrad": 40.8884}` |
| 26 | 59.5 | ir_card | `{"x": 1461.6295090390227, "z": 861.6295090390227, "height": 120.0}` |
| 27 | 60.0 | knob | `{"part": "mirror-1", "axis": "yaw", "delta_mrad": -16.4774}` |
| 28 | 60.5 | knob | `{"part": "mirror-1", "axis": "pitch", "delta_mrad": -20.0}` |
| 29 | 61.0 | ir_card | `{"x": 1461.6295090390227, "z": 861.6295090390227, "height": 120.0}` |
| 30 | 61.5 | knob | `{"part": "mirror-1", "axis": "pitch", "delta_mrad": -20.0}` |
| 31 | 62.0 | ir_card | `{"x": 1461.6295090390227, "z": 861.6295090390227, "height": 120.0}` |
| 32 | 67.0 | place | `{"part": "mirror-2", "x": 1461.6295090390227, "z": 861.6295090390227, "height": 120.0, "yaw_deg": 157.5}` |
| 33 | 67.5 | ir_card | `{"x": 1270.7106781186546, "z": 670.7106781186548, "height": 120.0}` |
| 34 | 68.0 | ir_card | `{"x": 1270.7106781186546, "z": 670.7106781186548, "height": 120.0}` |
| 35 | 68.5 | knob | `{"part": "mirror-2", "axis": "yaw", "delta_mrad": 11.1111}` |
| 36 | 69.0 | ir_card | `{"x": 1270.7106781186546, "z": 670.7106781186548, "height": 120.0}` |
| 37 | 69.6 | knob | `{"part": "mirror-2", "axis": "pitch", "delta_mrad": 11.1111}` |
| 38 | 70.1 | ir_card | `{"x": 1270.7106781186546, "z": 670.7106781186548, "height": 120.0}` |
| 39 | 70.6 | knob | `{"part": "mirror-2", "axis": "yaw", "delta_mrad": 10.5976}` |
| 40 | 71.1 | knob | `{"part": "mirror-2", "axis": "pitch", "delta_mrad": -15.0815}` |
| 41 | 71.6 | ir_card | `{"x": 1270.7106781186546, "z": 670.7106781186548, "height": 120.0}` |
| 42 | 72.1 | knob | `{"part": "mirror-2", "axis": "yaw", "delta_mrad": -0.4836}` |
| 43 | 72.6 | knob | `{"part": "mirror-2", "axis": "pitch", "delta_mrad": 2.5912}` |
| 44 | 73.1 | ir_card | `{"x": 1270.7106781186546, "z": 670.7106781186548, "height": 120.0}` |
| 45 | 73.3 | unblock | `{"arm": "800nm"}` |
| 46 | 78.3 | place | `{"part": "stage", "x": 891.6828996322961, "z": 306.0, "height": 120.0, "yaw_deg": 180.0}` |
| 47 | 78.8 | ir_card | `{"x": 1553.5533905932737, "z": 318.0, "height": 120.0}` |
| 48 | 83.8 | place | `{"part": "mirror-3", "x": 1553.5533905932737, "z": 319.9, "height": 119.3, "yaw_deg": 225.0}` |
| 49 | 84.3 | ir_card | `{"x": 1553.5533905932737, "z": 246.44660940672628, "height": 120.0}` |
| 50 | 84.8 | ir_card | `{"x": 1553.5533905932737, "z": 246.44660940672628, "height": 120.0}` |
| 51 | 85.3 | knob | `{"part": "mirror-3", "axis": "yaw", "delta_mrad": 40.8422}` |
| 52 | 85.8 | ir_card | `{"x": 1553.5533905932737, "z": 246.44660940672628, "height": 120.0}` |
| 53 | 86.3 | knob | `{"part": "mirror-3", "axis": "pitch", "delta_mrad": 40.8422}` |
| 54 | 86.8 | ir_card | `{"x": 1553.5533905932737, "z": 246.44660940672628, "height": 120.0}` |
| 55 | 87.3 | knob | `{"part": "mirror-3", "axis": "yaw", "delta_mrad": -20.0}` |
| 56 | 87.8 | knob | `{"part": "mirror-3", "axis": "pitch", "delta_mrad": -20.0}` |
| 57 | 88.3 | ir_card | `{"x": 1553.5533905932737, "z": 246.44660940672628, "height": 120.0}` |
| 58 | 88.8 | knob | `{"part": "mirror-3", "axis": "yaw", "delta_mrad": -17.8145}` |
| 59 | 89.3 | knob | `{"part": "mirror-3", "axis": "pitch", "delta_mrad": -15.4902}` |
| 60 | 89.8 | ir_card | `{"x": 1553.5533905932737, "z": 246.44660940672628, "height": 120.0}` |
| 61 | 90.3 | knob | `{"part": "mirror-3", "axis": "yaw", "delta_mrad": 2.3908}` |
| 62 | 90.8 | knob | `{"part": "mirror-3", "axis": "pitch", "delta_mrad": -4.5823}` |
| 63 | 91.3 | ir_card | `{"x": 1553.5533905932737, "z": 246.44660940672628, "height": 120.0}` |
| 64 | 96.3 | place | `{"part": "mirror-4", "x": 1553.5533905932737, "z": 246.44660940672628, "height": 120.0, "yaw_deg": 112.5}` |
| 65 | 96.9 | ir_card | `{"x": 1270.7106781186546, "z": 529.2893218813452, "height": 120.0}` |
| 66 | 97.4 | ir_card | `{"x": 1270.7106781186546, "z": 529.2893218813452, "height": 120.0}` |
| 67 | 97.9 | knob | `{"part": "mirror-4", "axis": "yaw", "delta_mrad": 7.5}` |
| 68 | 98.4 | ir_card | `{"x": 1270.7106781186546, "z": 529.2893218813452, "height": 120.0}` |
| 69 | 98.9 | knob | `{"part": "mirror-4", "axis": "pitch", "delta_mrad": 7.5}` |
| 70 | 99.4 | ir_card | `{"x": 1270.7106781186546, "z": 529.2893218813452, "height": 120.0}` |
| 71 | 99.9 | knob | `{"part": "mirror-4", "axis": "yaw", "delta_mrad": 10.6848}` |
| 72 | 100.4 | knob | `{"part": "mirror-4", "axis": "pitch", "delta_mrad": -6.956}` |
| 73 | 100.9 | ir_card | `{"x": 1270.7106781186546, "z": 529.2893218813452, "height": 120.0}` |
| 74 | 101.4 | knob | `{"part": "mirror-4", "axis": "yaw", "delta_mrad": 0.7422}` |
| 75 | 101.9 | knob | `{"part": "mirror-4", "axis": "pitch", "delta_mrad": -0.2337}` |
| 76 | 102.4 | ir_card | `{"x": 1270.7106781186546, "z": 529.2893218813452, "height": 120.0}` |
| 77 | 102.9 | knob | `{"part": "mirror-4", "axis": "yaw", "delta_mrad": 0.6506}` |
| 78 | 103.4 | knob | `{"part": "mirror-4", "axis": "pitch", "delta_mrad": -0.4811}` |
| 79 | 103.9 | ir_card | `{"x": 1270.7106781186546, "z": 529.2893218813452, "height": 120.0}` |
| 80 | 104.5 | knob | `{"part": "mirror-4", "axis": "yaw", "delta_mrad": -0.9131}` |
| 81 | 105.0 | knob | `{"part": "mirror-4", "axis": "pitch", "delta_mrad": 0.108}` |
| 82 | 105.5 | ir_card | `{"x": 1270.7106781186546, "z": 529.2893218813452, "height": 120.0}` |
| 83 | 105.7 | view_camera | `{"plane": "sample"}` |
| 84 | 105.9 | view_camera | `{"plane": "sample"}` |
| 85 | 106.5 | knob | `{"part": "mirror-4", "axis": "yaw", "delta_mrad": 0.3}` |
| 86 | 106.7 | view_camera | `{"plane": "sample"}` |
| 87 | 106.9 | view_camera | `{"plane": "sample"}` |
| 88 | 107.5 | knob | `{"part": "mirror-4", "axis": "pitch", "delta_mrad": 0.3}` |
| 89 | 107.7 | view_camera | `{"plane": "sample"}` |
| 90 | 107.9 | view_camera | `{"plane": "sample"}` |
| 91 | 108.5 | knob | `{"part": "mirror-4", "axis": "yaw", "delta_mrad": -0.4532}` |
| 92 | 109.0 | knob | `{"part": "mirror-4", "axis": "pitch", "delta_mrad": -0.0067}` |
| 93 | 109.3 | view_camera | `{"plane": "sample"}` |
| 94 | 109.4 | view_camera | `{"plane": "sample"}` |
| 95 | 110.0 | knob | `{"part": "mirror-4", "axis": "yaw", "delta_mrad": -0.0074}` |
| 96 | 110.5 | knob | `{"part": "mirror-4", "axis": "pitch", "delta_mrad": 0.0288}` |
| 97 | 110.8 | view_camera | `{"plane": "sample"}` |
| 98 | 110.9 | view_camera | `{"plane": "sample"}` |
| 99 | 113.9 | measure_path | `{"arm": "800nm"}` |
| 100 | 116.9 | measure_path | `{"arm": "opa"}` |
| 101 | 117.0 | status | `{}` |
| 102 | 145.3 | scan | `{"start_mm": 10.1, "end_mm": 22.1, "step_mm": 0.005, "t_int": 0.4}` |
| 103 | 149.6 | scan | `{"start_mm": 15.3285, "end_mm": 15.5515, "step_mm": 0.002, "t_int": 2.0}` |
| 104 | 149.7 | move_stage | `{"position_mm": 15.43691}` |
| 105 | 149.9 | view_camera | `{"plane": "sample"}` |
| 106 | 150.1 | view_camera | `{"plane": "sample"}` |
| 107 | 150.7 | knob | `{"part": "mirror-4", "axis": "pitch", "delta_mrad": -0.0158}` |
| 108 | 150.9 | view_camera | `{"plane": "sample"}` |
| 109 | 151.1 | view_camera | `{"plane": "sample"}` |
| 110 | 151.7 | knob | `{"part": "mirror-4", "axis": "yaw", "delta_mrad": -0.0229}` |
| 111 | 152.2 | knob | `{"part": "mirror-4", "axis": "pitch", "delta_mrad": 0.0256}` |
| 112 | 152.4 | view_camera | `{"plane": "sample"}` |
| 113 | 152.6 | view_camera | `{"plane": "sample"}` |
| 114 | 152.7 | submit | `{}` |
