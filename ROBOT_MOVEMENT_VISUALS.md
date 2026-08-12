# Go2 Movement Visuals

This document shows the movement flow for each robot control program in this repository.

## Legend

- `1002` balance stand
- `1003` stop move
- `1004` stand up
- `1007` euler body tilt
- `1008` move (walk/turn)
- `1009` sit
- `1016` hello wave
- `1017` stretch
- `1022` content (happy wag)

## demo.py

```mermaid
flowchart TD
    A[Connect] --> B[Set speed level 0]
    B --> C[Balance stand 1002]
    C --> D[Stand up 1004]
    D --> E[Content wag 1022]
    E --> F[Walk forward 0.1 m/s for 1.5s via 1008 loop]
    F --> G[Stop move 1003]
    G --> H[Disconnect]
```

## stand_wag_sit_example.py

```mermaid
flowchart TD
    A[Connect] --> B[Countdown 3s]
    B --> C[Stand up 1004]
    C --> D[Content wag 1022]
    D --> E[Sit 1009]
    E --> F[Disconnect]
```

## repeat_tilt_sit.py

```mermaid
flowchart TD
    A[Connect] --> B[Countdown]
    B --> C{Repeat 3x}
    C --> D[Tilt side 1 via 1007]
    D --> E[Tilt side 2 via 1007]
    E --> C
    C --> F[Sit 1009]
    F --> G[Disconnect]
```

## square_walk_sit.py

```mermaid
flowchart TD
    A[Connect] --> B[Stand up 1004]
    B --> C{For each of 4 sides}
    C --> D[Walk forward 3.0s at 0.3 m/s via 1008 loop]
    D --> E[Turn left in place 1.8s via 1008 loop]
    E --> C
    C --> F[Sit 1009]
    F --> G[Disconnect]
```

## walk_turn_walk_sit.py

```mermaid
flowchart TD
    A[Connect] --> B[Stand up 1004]
    B --> C[Walk forward 3.0s via 1008 loop]
    C --> D[Walk and turn for 2.0s via 1008 loop]
    D --> E[Walk forward 3.0s via 1008 loop]
    E --> F[Stop move 1003]
    F --> G[Sit 1009]
    G --> H[Disconnect]
```

## performance_routine.py

```mermaid
flowchart TD
    A[Connect] --> B[Countdown]
    B --> C[Balance stand 1002]
    C --> D[Sit 1009]
    D --> E[Stand up 1004]
    E --> F[Tilt right 1007]
    F --> G[Tilt left 1007]
    G --> H[Tilt right 1007]
    H --> I[Tilt left 1007]
    I --> J[Stretch 1017]
    J --> K[Walk forward 4.0s via 1008 loop]
    K --> L[Walk arc 2.5s via 1008 loop]
    L --> M[Walk forward 4.0s via 1008 loop]
    M --> N[Hello wave 1016]
    N --> O[Stop move 1003]
    O --> P[Sit 1009]
    P --> Q[Disconnect]
```

## pynput_teleop.py

```mermaid
flowchart TD
    A[Connect] --> B[Stand up 1004]
    B --> C[Keyboard control loop]

    C --> D{Key held}
    D -->|W| E[Send move x=+0.3 via 1008]
    D -->|S| F[Send move x=-0.3 via 1008]
    D -->|A| G[Send move z=+0.3 via 1008]
    D -->|D| H[Send move z=-0.3 via 1008]
    D -->|Space or timeout| I[Stop move 1003]
    D -->|Q| J[Stop move 1003 then sit 1009 and quit]

    E --> C
    F --> C
    G --> C
    H --> C
    I --> C
    J --> K[Disconnect]
```

## cli.py preset routines

```mermaid
flowchart LR
    A[greet] --> A1[balance -> hello -> content -> stop]
    B[calm-start] --> B1[speed 0 -> balance -> stand up -> stop]
    C[short-walk] --> C1[speed 0 -> balance -> walk_for_default 2s]
    D[reset] --> D1[stop -> balance -> stop]
    E[turn-left] --> E1[speed 0 -> balance -> walk_for turn +0.2]
    F[turn-right] --> F1[speed 0 -> balance -> walk_for turn -0.2]
    G[back-up-slowly] --> G1[speed 0 -> balance -> walk_for x=-0.08]
```
