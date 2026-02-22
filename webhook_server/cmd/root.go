package cmd

import (
	"fmt"
	"os"

	"github.com/spf13/cobra"
)

func NewCmdRoot() *cobra.Command {
	rootCmd := &cobra.Command{
		Use:   "Git-Tracker",
		Short: "A brief description of your CLI application",
		Long: `A longer description that explains your CLI application in detail, 
		including available commands and their usage.`,
		Run: func(cmd *cobra.Command, args []string) {
			fmt.Println("Welcome to Git-Tracker! Use --help for usage.")
		},
	}
	rootCmd.AddCommand(NewConfigCmd())
	rootCmd.AddCommand(NewRunCmd())
	return rootCmd
}

func Execute() {
	if err := NewCmdRoot().Execute(); err != nil {
		fmt.Println(err)
		os.Exit(1)
	}
}
