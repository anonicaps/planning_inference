from . import config
from .compilation import generate_auxiliary_programming_fluents
from .compilation import generate_extended_action

from .compilation import generate_reached_fluents
from .compilation import generate_sense_actions

from .compilation import generate_goal
from .compilation import generate_initial_state

from .pddl import Problem

from .parsers import parse_plan

import copy
import os



class DecodingTask(object):

    def __init__(self, planning_model, sensor_model, observation_sequence, hypothesis):
        self.planning_model = planning_model
        self.sensor_model = sensor_model
        self.observation_sequence = observation_sequence
        self.hypothesis = hypothesis

        self.compiled_model = self.__compile_model()
        self.compiled_problem = self.__compile_problem()

    def __compile_model(self):
        compiled_model = copy.deepcopy(self.planning_model)
        compiled_model.schemata = []

        indices = sorted(set(self.observation_sequence.observations.keys()).union(set(self.hypothesis.states.keys())))

        # Programming

        for scheme in self.planning_model.schemata:

            extended_action = generate_extended_action(scheme, False, False, False)


            compiled_model.schemata += [extended_action]

        auxiliary_programming_fluents = generate_auxiliary_programming_fluents()
        compiled_model.predicates += auxiliary_programming_fluents


        # Validation

        reached_fluents = generate_reached_fluents(indices)
        compiled_model.predicates += reached_fluents

        sense_actions = generate_sense_actions(self.observation_sequence, self.hypothesis, self.sensor_model)

        compiled_model.schemata += sense_actions

        return compiled_model


    def __compile_problem(self):

        init = generate_initial_state(self.hypothesis.states[0])

        goal = generate_goal()

        objects = self.hypothesis.objects


        return Problem(config.problem_file, self.planning_model.domain_name, objects, init, goal, use_metric=False)


    def decode(self, clean=True, planner="downward", t=3000):
        problem_file = config.problem_file
        domain_file = config.domain_file
        solution_file = config.solution_file
        log_file = config.log_file

        self.compiled_model.to_file(domain_file)
        self.compiled_problem.to_file(problem_file)

        if planner == "downward":
            planner_path = config.fast_downward_path

            cmd_args = [planner_path, '--plan-file %s' % solution_file, domain_file, problem_file, '--evaluator "lmc=merge_and_shrink(shrink_strategy=shrink_bisimulation(greedy=false),merge_strategy=merge_sccs(order_of_sccs=topological,merge_selector=score_based_filtering(scoring_functions=[goal_relevance,dfp,total_order])),label_reduction=exact(before_shrinking=true,before_merging=false),max_states=50k,threshold_before_merge=1)" --search "astar(lmc,lazy_evaluator=lmc)"']

        cmd = " ".join(cmd_args)
        cmd = "ulimit -t %d; " % t + cmd

        os.system(cmd)

        solution = parse_plan(solution_file)


        if clean:
            cmd = "rm %s; rm %s; rm %s; rm %s" % (domain_file, problem_file, solution_file, log_file)
            os.system(cmd)




        return solution